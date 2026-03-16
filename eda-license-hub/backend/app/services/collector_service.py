from __future__ import annotations

import asyncio
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import (
    LicenseCheckout,
    LicenseFeature,
    LicenseFileAsset,
    LicenseLogEvent,
    LicenseServer,
    LicenseUsageHistory,
    StaticLicenseGrant,
)
from app.services.flexlm_license_file_parser import FlexLMLicenseFileParser
from app.services.flexlm_log_parser import FlexLMLogParser
from app.services.flexlm_parser import FlexLMParser, ServerSnapshot


DEFAULT_LICENSE_DIR = Path('/eda/env/license')
DEFAULT_LICENSE_LOG_DIR = DEFAULT_LICENSE_DIR / 'log'
LMSTAT_LICENSE_PATH_RE = re.compile(r'License file\(s\) on [^:]+:\s*(?P<path>.+?\.(?:lic|dat|txt))(?::|\s*$)', re.IGNORECASE)


@dataclass
class CollectorResult:
    server_id: int
    server_name: str
    status: str
    feature_count: int
    source_type: str
    error: str | None = None


class CollectorService:
    def __init__(self) -> None:
        self.parser = FlexLMParser()
        self.license_file_parser = FlexLMLicenseFileParser()
        self.log_parser = FlexLMLogParser()

    async def collect_all(self, session: AsyncSession) -> list[CollectorResult]:
        stmt = (
            select(LicenseServer)
            .options(selectinload(LicenseServer.license_file_asset))
            .where(LicenseServer.status == 'active')
            .order_by(LicenseServer.id)
        )
        servers = (await session.execute(stmt)).scalars().all()
        results: list[CollectorResult] = []
        for server in servers:
            results.append(await self.collect_server(session, server))
        await session.commit()
        return results

    async def collect_single(self, session: AsyncSession, server_id: int) -> CollectorResult:
        stmt = select(LicenseServer).options(selectinload(LicenseServer.license_file_asset)).where(LicenseServer.id == server_id)
        server = (await session.execute(stmt)).scalar_one()
        result = await self.collect_server(session, server)
        await session.commit()
        return result

    async def collect_server(self, session: AsyncSession, server: LicenseServer) -> CollectorResult:
        try:
            raw_text = await self._fetch_raw_output(server)
            snapshot = self.parser.parse(raw_text)
            await self._persist_snapshot(session, server, snapshot)
            await self._sync_optional_static_assets(session, server, raw_text=raw_text)
            return CollectorResult(server.id, server.name, snapshot.status, len(snapshot.features), server.source_type)
        except Exception as exc:
            server.last_status = 'down'
            server.last_error = str(exc)
            return CollectorResult(server.id, server.name, 'down', 0, server.source_type, str(exc))

    async def _fetch_raw_output(self, server: LicenseServer) -> str:
        if server.source_type == 'sample_file':
            if not server.sample_path:
                raise ValueError('sample_path is required for sample_file source')
            raw_bytes = Path(server.sample_path).read_bytes()
            if raw_bytes.startswith(b'\xff\xfe') or raw_bytes.startswith(b'\xfe\xff'):
                return raw_bytes.decode('utf-16', errors='ignore')
            try:
                return raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return raw_bytes.decode('latin-1', errors='ignore')

        executable = server.lmutil_path or 'lmutil'
        args = shlex.split(server.lmstat_args or '')
        if not args:
            args = ['lmstat', '-a', '-c', f'{server.port}@{server.host}']
        proc = await asyncio.create_subprocess_exec(
            executable,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=settings.collector_timeout_seconds)
        if proc.returncode != 0:
            raise RuntimeError(stderr.decode('utf-8', errors='ignore') or f'lmutil exit code {proc.returncode}')
        return stdout.decode('utf-8', errors='ignore')

    async def _persist_snapshot(self, session: AsyncSession, server: LicenseServer, snapshot: ServerSnapshot) -> None:
        server.last_status = snapshot.status
        server.last_check_time = snapshot.collected_at
        server.last_error = None

        existing_stmt = (
            select(LicenseFeature)
            .options(selectinload(LicenseFeature.checkouts))
            .where(LicenseFeature.server_id == server.id)
        )
        existing = (await session.execute(existing_stmt)).scalars().all()
        existing_map = {feature.feature_name: feature for feature in existing}
        seen_names: set[str] = set()

        for feature_snapshot in snapshot.features:
            feature = existing_map.get(feature_snapshot.feature_name)
            if feature is None:
                feature = LicenseFeature(
                    server_id=server.id,
                    feature_name=feature_snapshot.feature_name,
                    vendor=server.vendor,
                )
                session.add(feature)
                await session.flush()

            feature.total_licenses = feature_snapshot.total_licenses
            feature.used_licenses = feature_snapshot.used_licenses
            feature.available_licenses = feature_snapshot.available_licenses
            feature.usage_percentage = feature_snapshot.usage_percentage
            feature.raw_block = feature_snapshot.raw_block
            seen_names.add(feature.feature_name)

            await session.execute(delete(LicenseCheckout).where(LicenseCheckout.feature_id == feature.id))
            for checkout in feature_snapshot.checkouts:
                session.add(LicenseCheckout(
                    feature_id=feature.id,
                    username=checkout.username,
                    hostname=checkout.hostname,
                    display=checkout.display,
                    process_info=checkout.process_info,
                    checkout_time=checkout.checkout_time,
                    server_handle=checkout.server_handle,
                    is_active=True,
                ))
            session.add(LicenseUsageHistory(
                feature_id=feature.id,
                timestamp=snapshot.collected_at,
                used_count=feature_snapshot.used_licenses,
                available_count=feature_snapshot.available_licenses,
                usage_percentage=feature_snapshot.usage_percentage,
            ))

        for feature in existing:
            if feature.feature_name not in seen_names:
                await session.delete(feature)

    async def _sync_optional_static_assets(self, session: AsyncSession, server: LicenseServer, *, raw_text: str | None = None) -> None:
        license_file_path = self._resolve_license_file_path(server, raw_text=raw_text)
        if license_file_path:
            try:
                await self._persist_license_file(session, server, license_file_path)
            except Exception as exc:
                server.static_grants_parse_error = str(exc)
        if not license_file_path:
            server.static_grants_parse_error = None

        license_log_path = self._resolve_license_log_path(server)
        if license_log_path:
            try:
                await self._persist_license_log(session, server, license_log_path)
            except Exception as exc:
                server.log_parse_error = str(exc)
        if not license_log_path:
            server.log_parse_error = None

    def _resolve_license_file_path(self, server: LicenseServer, *, raw_text: str | None = None) -> str | None:
        explicit = self._normalize_existing_path(server.license_file_path)
        if explicit:
            return explicit

        discovered_from_output = self._discover_license_file_from_lmstat(raw_text)
        if discovered_from_output:
            return discovered_from_output

        candidates = self._find_matching_files(
            DEFAULT_LICENSE_DIR,
            stems=self._path_match_tokens(server),
            suffixes={'.dat', '.lic', '.txt'},
            exclude_dirs={DEFAULT_LICENSE_LOG_DIR},
        )
        return str(candidates[0]) if len(candidates) == 1 else None

    def _resolve_license_log_path(self, server: LicenseServer) -> str | None:
        explicit = self._normalize_existing_path(server.license_log_path)
        if explicit:
            return explicit

        candidates = self._find_matching_files(
            DEFAULT_LICENSE_LOG_DIR,
            stems=self._path_match_tokens(server),
            suffixes={'.log', '.txt'},
            exclude_dirs=set(),
        )
        return str(candidates[0]) if len(candidates) == 1 else None

    def _discover_license_file_from_lmstat(self, raw_text: str | None) -> str | None:
        if not raw_text:
            return None
        match = LMSTAT_LICENSE_PATH_RE.search(raw_text)
        if not match:
            return None
        return self._normalize_existing_path(match.group('path').strip())

    def _path_match_tokens(self, server: LicenseServer) -> set[str]:
        values = [server.vendor, server.name, server.host, f'{server.vendor}_{server.host}' if server.vendor and server.host else None]
        tokens: set[str] = set()
        for value in values:
            if not value:
                continue
            normalized = re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')
            if normalized:
                tokens.add(normalized)
        return tokens

    def _find_matching_files(
        self,
        root: Path,
        *,
        stems: set[str],
        suffixes: set[str],
        exclude_dirs: set[Path],
    ) -> list[Path]:
        if not root.exists() or not stems:
            return []

        excluded = {path.resolve() for path in exclude_dirs if path.exists()}
        matches: list[Path] = []
        for item in root.iterdir():
            if item.is_dir() and item.resolve() in excluded:
                continue
            if not item.is_file():
                continue
            if item.suffix.lower() not in suffixes:
                continue
            normalized_stem = re.sub(r'[^a-z0-9]+', '_', item.stem.lower()).strip('_')
            if normalized_stem in stems or any(token in normalized_stem for token in stems):
                matches.append(item)
        return sorted(matches)

    def _normalize_existing_path(self, file_path: str | None) -> str | None:
        if not file_path:
            return None
        path = Path(file_path)
        return str(path) if path.exists() and path.is_file() else None

    async def _persist_license_file(self, session: AsyncSession, server: LicenseServer, license_file_path: str) -> None:
        raw_text = self._read_text_file(license_file_path)
        parsed = self.license_file_parser.parse(raw_text)

        asset = server.license_file_asset
        if asset is None:
            asset = LicenseFileAsset(server_id=server.id)
            session.add(asset)
            await session.flush()

        asset.source_path = license_file_path
        asset.server_name = parsed.server.host if parsed.server else None
        asset.server_hostid = parsed.server.hostid if parsed.server else None
        asset.server_port = parsed.server.port if parsed.server else None
        asset.daemon_name = parsed.daemon.name if parsed.daemon else None
        asset.daemon_path = parsed.daemon.path if parsed.daemon else None
        asset.options_path = parsed.daemon.options_path if parsed.daemon else None
        asset.raw_header = '\n'.join(
            part for part in [parsed.server.raw_record if parsed.server else None, parsed.daemon.raw_record if parsed.daemon else None] if part
        ) or None
        asset.last_parsed_at = parsed.parsed_at

        await session.execute(delete(StaticLicenseGrant).where(StaticLicenseGrant.server_id == server.id))
        for grant in parsed.grants:
            session.add(StaticLicenseGrant(
                server_id=server.id,
                license_file_asset_id=asset.id,
                record_type=grant.record_type,
                vendor_name=grant.vendor_name,
                feature_name=grant.feature_name,
                version=grant.version,
                quantity=grant.quantity,
                issued_date=grant.issued_date,
                start_date=grant.start_date,
                expiry_date=grant.expiry_date,
                expiry_text=grant.expiry_text,
                serial_number=grant.serial_number,
                notice=grant.notice,
                raw_record=grant.raw_record,
            ))

        server.static_grants_last_parsed_at = parsed.parsed_at
        server.static_grants_parse_error = None

    async def _persist_license_log(self, session: AsyncSession, server: LicenseServer, license_log_path: str) -> None:
        raw_text = self._read_text_file(license_log_path)
        parsed = self.log_parser.parse(raw_text)

        existing_hashes = set(
            (await session.execute(select(LicenseLogEvent.event_hash).where(LicenseLogEvent.server_id == server.id))).scalars().all()
        )
        for event in parsed.events:
            if event.event_hash in existing_hashes:
                continue
            session.add(LicenseLogEvent(
                server_id=server.id,
                event_type=event.event_type,
                event_time=event.event_time,
                vendor_daemon=event.vendor_daemon,
                feature_name=event.feature_name,
                username=event.username,
                hostname=event.hostname,
                display=event.display,
                event_hash=event.event_hash,
                raw_line=event.raw_line,
            ))

        server.log_last_parsed_at = parsed.parsed_at
        server.log_parse_error = None

    def _read_text_file(self, file_path: str | None) -> str:
        if not file_path:
            raise ValueError('file path is required')
        raw_bytes = Path(file_path).read_bytes()
        if raw_bytes.startswith(b'\xff\xfe') or raw_bytes.startswith(b'\xfe\xff'):
            return raw_bytes.decode('utf-16', errors='ignore')
        try:
            return raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return raw_bytes.decode('latin-1', errors='ignore')


collector_service = CollectorService()
