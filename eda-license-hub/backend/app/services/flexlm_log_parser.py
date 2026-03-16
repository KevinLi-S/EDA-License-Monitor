from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime


EVENT_RE = re.compile(
    r'^(?P<time>\d{1,2}:\d{2}:\d{2})\s+\((?P<vendor>[^)]+)\)\s+(?P<type>OUT|IN|DENIED):\s+"(?P<feature>[^"]+)"\s+(?P<identity>[^\s]+)(?:\s+(?P<tail>.*))?$',
    re.IGNORECASE,
)
IDENTITY_RE = re.compile(r'(?P<user>[^@\s]+)@(?P<host>[^\s:]+)(?::(?P<display>.+))?')


@dataclass
class LicenseLogEventRecord:
    event_type: str
    event_time: datetime | None
    vendor_daemon: str | None
    feature_name: str | None
    username: str | None
    hostname: str | None
    display: str | None
    raw_line: str
    event_hash: str


@dataclass
class ParsedLicenseLog:
    events: list[LicenseLogEventRecord] = field(default_factory=list)
    parsed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_text: str = ''


class FlexLMLogParser:
    def parse(self, raw_text: str, *, reference_date: datetime | None = None) -> ParsedLicenseLog:
        parsed = ParsedLicenseLog(raw_text=raw_text)
        ref = reference_date or datetime.now(UTC)

        for line in raw_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = EVENT_RE.match(stripped)
            if not match:
                continue
            event_time = self._combine_time(ref, match.group('time'))
            identity_match = IDENTITY_RE.match(match.group('identity'))
            username = identity_match.group('user') if identity_match else None
            hostname = identity_match.group('host') if identity_match else None
            display = identity_match.group('display') if identity_match else None
            parsed.events.append(
                LicenseLogEventRecord(
                    event_type=match.group('type').upper(),
                    event_time=event_time,
                    vendor_daemon=match.group('vendor'),
                    feature_name=match.group('feature'),
                    username=username,
                    hostname=hostname,
                    display=display,
                    raw_line=stripped,
                    event_hash=self._hash_line(stripped),
                )
            )

        return parsed

    def _combine_time(self, reference: datetime, clock_text: str) -> datetime | None:
        try:
            clock = datetime.strptime(clock_text, '%H:%M:%S').time()
        except ValueError:
            return None
        return datetime.combine(reference.date(), clock, tzinfo=reference.tzinfo or UTC)

    def _hash_line(self, raw_line: str) -> str:
        return hashlib.sha256(raw_line.encode('utf-8')).hexdigest()
