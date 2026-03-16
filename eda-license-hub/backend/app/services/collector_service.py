from __future__ import annotations

import asyncio
import shlex
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import LicenseCheckout, LicenseFeature, LicenseServer, LicenseUsageHistory
from app.services.flexlm_parser import FlexLMParser, ServerSnapshot


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

    async def collect_all(self, session: AsyncSession) -> list[CollectorResult]:
        stmt = select(LicenseServer).where(LicenseServer.status == 'active').order_by(LicenseServer.id)
        servers = (await session.execute(stmt)).scalars().all()
        results: list[CollectorResult] = []
        for server in servers:
            results.append(await self.collect_server(session, server))
        await session.commit()
        return results

    async def collect_single(self, session: AsyncSession, server_id: int) -> CollectorResult:
        stmt = select(LicenseServer).where(LicenseServer.id == server_id)
        server = (await session.execute(stmt)).scalar_one()
        result = await self.collect_server(session, server)
        await session.commit()
        return result

    async def collect_server(self, session: AsyncSession, server: LicenseServer) -> CollectorResult:
        try:
            raw_text = await self._fetch_raw_output(server)
            snapshot = self.parser.parse(raw_text)
            await self._persist_snapshot(session, server, snapshot)
            return CollectorResult(server.id, server.name, snapshot.status, len(snapshot.features), server.source_type)
        except Exception as exc:
            server.last_status = 'down'
            server.last_error = str(exc)
            return CollectorResult(server.id, server.name, 'down', 0, server.source_type, str(exc))

    async def _fetch_raw_output(self, server: LicenseServer) -> str:
        if server.source_type == 'sample_file':
            if not server.sample_path:
                raise ValueError('sample_path is required for sample_file source')
            return Path(server.sample_path).read_text(encoding='utf-8')

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


collector_service = CollectorService()
