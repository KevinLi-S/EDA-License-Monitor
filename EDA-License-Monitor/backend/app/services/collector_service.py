from __future__ import annotations

import asyncio
import os
import re
import select as select_module
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import AsyncSessionLocal
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
LMSTAT_LICENSE_PATH_LINE_RE = re.compile(r'License file\(s\) on [^:]+:\s*(?P<paths>.+)$', re.IGNORECASE)
LMSTAT_LICENSE_PATH_TOKEN_RE = re.compile(r'((?:[A-Za-z]:[\\/]|/)[^\s,;]+?\.(?:lic|dat|txt))', re.IGNORECASE)


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

    async def collect_all(
        self,
        session: AsyncSession,
        *,
        sync_static_assets: bool = True,
        parallel: bool = False,
    ) -> list[CollectorResult]:
        if parallel:
            server_ids = await self._list_active_server_ids(session)
            return await self._collect_server_ids(server_ids, sync_static_assets=sync_static_assets)

        stmt = (
            select(LicenseServer)
            .options(selectinload(LicenseServer.license_file_asset))
            .where(LicenseServer.status == 'active')
            .order_by(LicenseServer.id)
        )
        servers = (await session.execute(stmt)).scalars().all()
        results: list[CollectorResult] = []
        for server in servers:
            results.append(await self.collect_server(session, server, sync_static_assets=sync_static_assets))
        await session.commit()
        return results

    async def collect_single(self, session: AsyncSession, server_id: int, *, sync_static_assets: bool = True) -> CollectorResult:
        stmt = select(LicenseServer).options(selectinload(LicenseServer.license_file_asset)).where(LicenseServer.id == server_id)
        server = (await session.execute(stmt)).scalar_one()
        result = await self.collect_server(session, server, sync_static_assets=sync_static_assets)
        await session.commit()
        return result

    async def collect_realtime_usage(self, session: AsyncSession) -> list[CollectorResult]:
        server_ids = await self._list_active_server_ids(session)
        return await self._collect_server_ids(server_ids, sync_static_assets=False)

    async def refresh_log_usage(self, session: AsyncSession) -> list[CollectorResult]:
        server_ids = await self._list_active_server_ids(session)
        if not server_ids:
            return []

        async def _refresh_one(server_id: int) -> CollectorResult:
            async with AsyncSessionLocal() as isolated_session:
                stmt = (
                    select(LicenseServer)
                    .options(selectinload(LicenseServer.license_file_asset))
                    .where(LicenseServer.id == server_id)
                )
                server = (await isolated_session.execute(stmt)).scalar_one()
                try:
                    license_log_path = self._resolve_license_log_path(server)
                    if not license_log_path:
                        server.log_parse_error = None
                        await isolated_session.commit()
                        feature_count = await self._count_server_features(isolated_session, server.id)
                        return CollectorResult(server.id, server.name, server.last_status or 'unknown', feature_count, server.source_type)

                    parsed_log = await self._persist_license_log(isolated_session, server, license_log_path)
                    await self._rebuild_active_usage_from_logs(
                        isolated_session,
                        server,
                        parsed_log,
                        update_feature_totals=False,
                    )
                    await isolated_session.commit()
                    feature_count = await self._count_server_features(isolated_session, server.id)
                    return CollectorResult(server.id, server.name, server.last_status or 'ok', feature_count, server.source_type)
                except Exception as exc:
                    server.log_parse_error = str(exc)
                    await isolated_session.commit()
                    feature_count = await self._count_server_features(isolated_session, server.id)
                    return CollectorResult(server.id, server.name, 'down', feature_count, server.source_type, str(exc))

        return list(await asyncio.gather(*(_refresh_one(server_id) for server_id in server_ids)))

    async def collect_server(self, session: AsyncSession, server: LicenseServer, *, sync_static_assets: bool = True) -> CollectorResult:
        raw_text: str | None = None
        snapshot = None
        snapshot_error: Exception | None = None

        try:
            raw_text = await self._fetch_raw_output(server)
            snapshot = self.parser.parse(raw_text)
            await self._persist_snapshot(session, server, snapshot)
        except Exception as exc:
            snapshot_error = exc
            server.last_status = 'down'
            server.last_error = str(exc)

        if sync_static_assets:
            await self._sync_optional_static_assets(
                session,
                server,
                raw_text=raw_text,
                rebuild_usage_from_logs=snapshot is None,
            )

        feature_count = await self._count_server_features(session, server.id)
        if snapshot is not None:
            return CollectorResult(server.id, server.name, snapshot.status, feature_count, server.source_type)
        if feature_count > 0 and server.log_last_parsed_at is not None:
            return CollectorResult(server.id, server.name, 'degraded', feature_count, server.source_type, str(snapshot_error) if snapshot_error else None)
        return CollectorResult(server.id, server.name, 'down', feature_count, server.source_type, str(snapshot_error) if snapshot_error else None)

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

    async def _run_lmutil_command(self, executable: str, args: list[str]) -> str:
        if os.name == 'nt':
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

        stdout, returncode = await asyncio.to_thread(
            self._run_lmutil_with_pty_sync,
            executable,
            args,
            settings.collector_timeout_seconds,
        )
        if stdout.strip():
            return stdout
        if returncode not in (0, None):
            raise RuntimeError(stdout or f'lmutil exit code {returncode}')
        return stdout

    def _run_lmutil_with_pty_sync(self, executable: str, args: list[str], timeout_seconds: int | float) -> tuple[str, int | None]:
        import pty

        master_fd, slave_fd = pty.openpty()
        env = os.environ.copy()
        env.setdefault('TERM', 'xterm')
        env.setdefault('LINES', '50')
        env.setdefault('COLUMNS', '160')
        proc = subprocess.Popen(
            [executable, *args],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            env=env,
        )
        os.close(slave_fd)

        chunks: list[bytes] = []
        deadline = time.monotonic() + float(timeout_seconds)
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select_module.select([master_fd], [], [], 0.2)
                if master_fd in ready:
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    chunks.append(data)
                if proc.poll() is not None:
                    break

            if proc.poll() is None:
                proc.terminate()
                time.sleep(0.5)
                if proc.poll() is None:
                    proc.kill()

            while True:
                ready, _, _ = select_module.select([master_fd], [], [], 0)
                if master_fd not in ready:
                    break
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                chunks.append(data)
        finally:
            os.close(master_fd)

        return b''.join(chunks).decode('utf-8', errors='ignore'), proc.returncode

    def _build_lmutil_hostname_fallback_args(self, server: LicenseServer, args: list[str]) -> list[str]:
        hostname = None
        if server.license_file_asset and server.license_file_asset.server_name:
            hostname = server.license_file_asset.server_name.strip()
        if not hostname or hostname == server.host:
            return args

        expected_target = f'{server.port}@{server.host}' if server.port and server.host else None
        replacement_target = f'{server.port}@{hostname}' if server.port else hostname

        patched = list(args)
        for idx, token in enumerate(patched):
            if expected_target and token == expected_target:
                patched[idx] = replacement_target
                return patched
            if expected_target and expected_target in token:
                patched[idx] = token.replace(expected_target, replacement_target)
                return patched

        if not patched:
            return ['lmstat', '-a', '-c', replacement_target]
        return patched

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

    async def _sync_optional_static_assets(
        self,
        session: AsyncSession,
        server: LicenseServer,
        *,
        raw_text: str | None = None,
        rebuild_usage_from_logs: bool = False,
    ) -> None:
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
                parsed_log = await self._persist_license_log(session, server, license_log_path)
                await self._rebuild_active_usage_from_logs(
                    session,
                    server,
                    parsed_log,
                    update_feature_totals=rebuild_usage_from_logs,
                )
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

        candidates: list[str] = []
        for line in raw_text.splitlines():
            match = LMSTAT_LICENSE_PATH_LINE_RE.search(line)
            if not match:
                continue
            for token in LMSTAT_LICENSE_PATH_TOKEN_RE.findall(match.group('paths')):
                normalized = self._normalize_existing_path(token.strip())
                if normalized:
                    candidates.append(normalized)

        return candidates[0] if candidates else None

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
        seen_identity: set[tuple[str, str, str | None, object | None, str | None]] = set()
        for grant in parsed.grants:
            identity = (
                grant.feature_name,
                grant.record_type,
                grant.version,
                grant.expiry_date,
                grant.serial_number,
            )
            if identity in seen_identity:
                continue
            seen_identity.add(identity)

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

    async def _persist_license_log(self, session: AsyncSession, server: LicenseServer, license_log_path: str):
        raw_text = self._read_text_file(license_log_path)
        parsed = self.log_parser.parse(raw_text)

        existing_hashes = set(
            (await session.execute(select(LicenseLogEvent.event_hash).where(LicenseLogEvent.server_id == server.id))).scalars().all()
        )
        seen_hashes = set(existing_hashes)
        for event in parsed.events:
            if event.event_hash in seen_hashes:
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
            seen_hashes.add(event.event_hash)

        server.log_last_parsed_at = parsed.parsed_at
        server.log_parse_error = None
        return parsed

    async def _rebuild_active_usage_from_logs(
        self,
        session: AsyncSession,
        server: LicenseServer,
        parsed_log,
        *,
        update_feature_totals: bool = False,
    ) -> None:
        active_stack: dict[tuple[str, str, str], list] = {}
        for event in parsed_log.events:
            if event.event_type not in {'OUT', 'IN'} or not event.feature_name or not event.username or not event.hostname:
                continue
            key = (event.feature_name, event.username, event.hostname)
            active_stack.setdefault(key, [])
            if event.event_type == 'OUT':
                active_stack[key].append(event)
            elif active_stack[key]:
                active_stack[key].pop()

        active_feature_names = sorted({feature_name for (feature_name, _, _), stack in active_stack.items() if stack})

        if update_feature_totals:
            feature_stmt = select(LicenseFeature).where(LicenseFeature.server_id == server.id)
            features = (await session.execute(feature_stmt)).scalars().all()
            feature_map = {feature.feature_name: feature for feature in features}

            grant_stmt = select(StaticLicenseGrant).where(StaticLicenseGrant.server_id == server.id)
            static_grants = (await session.execute(grant_stmt)).scalars().all()
            grant_total_by_feature: dict[str, int] = {}
            for grant in static_grants:
                if not grant.feature_name or grant.quantity is None:
                    continue
                grant_total_by_feature[grant.feature_name] = max(grant_total_by_feature.get(grant.feature_name, 0), int(grant.quantity))
        else:
            feature_map: dict[str, LicenseFeature] = {}
            if active_feature_names:
                feature_stmt = select(LicenseFeature).where(
                    LicenseFeature.server_id == server.id,
                    LicenseFeature.feature_name.in_(active_feature_names),
                )
                features = (await session.execute(feature_stmt)).scalars().all()
                feature_map = {feature.feature_name: feature for feature in features}
            grant_total_by_feature = {}

        await session.flush()
        feature_ids_subquery = select(LicenseFeature.id).where(LicenseFeature.server_id == server.id)
        await session.execute(delete(LicenseCheckout).where(LicenseCheckout.feature_id.in_(feature_ids_subquery)))

        active_count_by_feature: dict[str, int] = {}
        for (feature_name, username, hostname), stack in active_stack.items():
            if not stack:
                continue
            feature = feature_map.get(feature_name)
            if feature is None:
                total_licenses = grant_total_by_feature.get(feature_name, 0)
                feature = LicenseFeature(
                    server_id=server.id,
                    feature_name=feature_name,
                    vendor=server.vendor,
                    total_licenses=total_licenses,
                    used_licenses=0,
                    available_licenses=max(total_licenses, 0),
                    usage_percentage=0,
                )
                session.add(feature)
                await session.flush()
                feature_map[feature_name] = feature
            for event in stack:
                session.add(LicenseCheckout(
                    feature_id=feature.id,
                    username=username,
                    hostname=hostname,
                    display=event.display,
                    process_info=event.raw_line,
                    checkout_time=event.event_time,
                    server_handle=None,
                    is_active=True,
                ))
            active_count_by_feature[feature_name] = active_count_by_feature.get(feature_name, 0) + len(stack)

        if update_feature_totals:
            for feature in feature_map.values():
                used = active_count_by_feature.get(feature.feature_name, 0)
                feature.used_licenses = used
                feature.available_licenses = max((feature.total_licenses or 0) - used, 0)
                feature.usage_percentage = (used / feature.total_licenses * 100) if feature.total_licenses else 0

    async def _list_active_server_ids(self, session: AsyncSession) -> list[int]:
        stmt = (
            select(LicenseServer.id)
            .where(LicenseServer.status == 'active')
            .order_by(LicenseServer.id)
        )
        return list((await session.execute(stmt)).scalars().all())

    async def _collect_server_ids(self, server_ids: list[int], *, sync_static_assets: bool) -> list[CollectorResult]:
        if not server_ids:
            return []

        async def _collect_one(server_id: int) -> CollectorResult:
            async with AsyncSessionLocal() as isolated_session:
                return await self.collect_single(isolated_session, server_id, sync_static_assets=sync_static_assets)

        return list(await asyncio.gather(*(_collect_one(server_id) for server_id in server_ids)))

    async def _count_server_features(self, session: AsyncSession, server_id: int) -> int:
        stmt = select(LicenseFeature.id).where(LicenseFeature.server_id == server_id)
        return len((await session.execute(stmt)).scalars().all())

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
