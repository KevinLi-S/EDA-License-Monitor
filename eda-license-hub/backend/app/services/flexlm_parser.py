from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime


FEATURE_RE = re.compile(
    r"Users of (?P<name>[^:]+):\s*\(Total of (?P<total>\d+) licenses? issued;\s*Total of (?P<used>\d+) licenses? in use\)",
    re.IGNORECASE,
)
CHECKOUT_RE = re.compile(
    r"^\s*(?P<user>[^\s]+)\s+(?P<host>[^\s]+)\s+(?P<display>[^\s]+)?\s*\((?P<handle>[^\)]+)\)\s*(?P<checkout>start.*)?$",
    re.IGNORECASE,
)
SERVER_UP_RE = re.compile(r"license server UP", re.IGNORECASE)
VENDOR_STATUS_RE = re.compile(r"(?P<vendor>[A-Za-z0-9_\-]+):\s+(?P<status>UP|DOWN)", re.IGNORECASE)


@dataclass
class CheckoutRecord:
    username: str
    hostname: str
    display: str | None = None
    server_handle: str | None = None
    checkout_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    process_info: str | None = None


@dataclass
class FeatureSnapshot:
    feature_name: str
    total_licenses: int
    used_licenses: int
    available_licenses: int
    usage_percentage: float
    raw_block: str
    checkouts: list[CheckoutRecord] = field(default_factory=list)


@dataclass
class ServerSnapshot:
    status: str
    vendor_status: dict[str, str]
    features: list[FeatureSnapshot]
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_output: str = ''


class FlexLMParser:
    def parse(self, raw_text: str) -> ServerSnapshot:
        lines = raw_text.splitlines()
        vendor_status: dict[str, str] = {}
        status = 'down'
        features: list[FeatureSnapshot] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            if SERVER_UP_RE.search(line):
                status = 'up'
            vendor_match = VENDOR_STATUS_RE.search(line)
            if vendor_match:
                vendor_status[vendor_match.group('vendor').lower()] = vendor_match.group('status').lower()
                if vendor_match.group('status').lower() == 'up':
                    status = 'up'

            feature_match = FEATURE_RE.search(line)
            if not feature_match:
                i += 1
                continue

            block_lines = [line]
            checkouts: list[CheckoutRecord] = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if FEATURE_RE.search(next_line):
                    i -= 1
                    break
                if next_line.strip().startswith('Users of '):
                    i -= 1
                    break
                block_lines.append(next_line)
                checkout_match = CHECKOUT_RE.match(next_line)
                if checkout_match and checkout_match.group('user'):
                    checkouts.append(
                        CheckoutRecord(
                            username=checkout_match.group('user'),
                            hostname=checkout_match.group('host'),
                            display=checkout_match.group('display'),
                            server_handle=checkout_match.group('handle'),
                            process_info=next_line.strip(),
                        )
                    )
                i += 1

            total = int(feature_match.group('total'))
            used = int(feature_match.group('used'))
            features.append(
                FeatureSnapshot(
                    feature_name=feature_match.group('name').strip(),
                    total_licenses=total,
                    used_licenses=used,
                    available_licenses=max(total - used, 0),
                    usage_percentage=round((used / total) * 100, 2) if total else 0.0,
                    raw_block='\n'.join(block_lines),
                    checkouts=checkouts,
                )
            )
            i += 1

        return ServerSnapshot(status=status, vendor_status=vendor_status, features=features, raw_output=raw_text)
