from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from datetime import UTC, date, datetime


SUPPORTED_RECORD_TYPES = {'SERVER', 'DAEMON', 'VENDOR', 'FEATURE', 'INCREMENT'}


@dataclass
class LicenseServerLine:
    host: str
    hostid: str
    port: str | None = None
    raw_record: str = ''


@dataclass
class LicenseDaemonLine:
    name: str
    path: str | None = None
    options_path: str | None = None
    raw_record: str = ''


@dataclass
class LicenseGrantRecord:
    record_type: str
    feature_name: str
    vendor_name: str | None
    version: str | None
    quantity: int | None
    expiry_date: date | None
    expiry_text: str | None
    issued_date: date | None = None
    start_date: date | None = None
    serial_number: str | None = None
    notice: str | None = None
    raw_record: str = ''
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class ParsedLicenseFile:
    server: LicenseServerLine | None = None
    daemon: LicenseDaemonLine | None = None
    grants: list[LicenseGrantRecord] = field(default_factory=list)
    parsed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_text: str = ''


class FlexLMLicenseFileParser:
    def parse(self, raw_text: str) -> ParsedLicenseFile:
        logical_lines = self._join_continuations(raw_text)
        parsed = ParsedLicenseFile(raw_text=raw_text)

        for line in logical_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            tokens = shlex.split(stripped, posix=True)
            if not tokens:
                continue

            record_type = tokens[0].upper()
            if record_type not in SUPPORTED_RECORD_TYPES:
                continue

            if record_type == 'SERVER':
                parsed.server = self._parse_server(tokens, stripped)
            elif record_type in {'DAEMON', 'VENDOR'}:
                parsed.daemon = self._parse_daemon(tokens, stripped)
            else:
                parsed.grants.append(self._parse_grant(tokens, stripped))

        return parsed

    def _join_continuations(self, raw_text: str) -> list[str]:
        logical_lines: list[str] = []
        buffer = ''
        for raw_line in raw_text.splitlines():
            line = raw_line.rstrip()
            if not line:
                if buffer:
                    logical_lines.append(buffer.strip())
                    buffer = ''
                continue
            if line.endswith('\\'):
                buffer += line[:-1].rstrip() + ' '
                continue
            buffer += line
            logical_lines.append(buffer.strip())
            buffer = ''
        if buffer:
            logical_lines.append(buffer.strip())
        return logical_lines

    def _parse_server(self, tokens: list[str], raw_record: str) -> LicenseServerLine:
        port = tokens[3] if len(tokens) > 3 else None
        return LicenseServerLine(
            host=tokens[1] if len(tokens) > 1 else '',
            hostid=tokens[2] if len(tokens) > 2 else '',
            port=port,
            raw_record=raw_record,
        )

    def _parse_daemon(self, tokens: list[str], raw_record: str) -> LicenseDaemonLine:
        options_path = None
        for token in tokens[3:]:
            if token.lower().startswith('options='):
                options_path = token.split('=', 1)[1]
        return LicenseDaemonLine(
            name=tokens[1] if len(tokens) > 1 else '',
            path=tokens[2] if len(tokens) > 2 and not tokens[2].lower().startswith('options=') else None,
            options_path=options_path,
            raw_record=raw_record,
        )

    def _parse_grant(self, tokens: list[str], raw_record: str) -> LicenseGrantRecord:
        attrs: dict[str, str] = {}
        for token in tokens[6:]:
            if '=' in token:
                key, value = token.split('=', 1)
                attrs[key.lower()] = value

        expiry_text = tokens[4] if len(tokens) > 4 else None
        quantity_text = tokens[5] if len(tokens) > 5 else None
        return LicenseGrantRecord(
            record_type=tokens[0].upper(),
            feature_name=tokens[1] if len(tokens) > 1 else '',
            vendor_name=tokens[2] if len(tokens) > 2 else None,
            version=tokens[3] if len(tokens) > 3 else None,
            expiry_date=self._parse_date(expiry_text),
            expiry_text=expiry_text,
            quantity=self._parse_int(quantity_text),
            issued_date=self._parse_date(attrs.get('issued')),
            start_date=self._parse_date(attrs.get('start')),
            serial_number=attrs.get('serial') or attrs.get('sn'),
            notice=attrs.get('notice'),
            raw_record=raw_record,
            attributes=attrs,
        )

    def _parse_date(self, value: str | None) -> date | None:
        if not value:
            return None
        lowered = value.lower()
        if lowered in {'permanent', 'none'}:
            return None
        for fmt in ('%d-%b-%Y', '%d-%b-%y', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_int(self, value: str | None) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None
