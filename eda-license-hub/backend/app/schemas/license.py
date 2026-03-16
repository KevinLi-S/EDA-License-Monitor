from datetime import date, datetime

from pydantic import BaseModel


class LicenseFileAssetSummary(BaseModel):
    id: int
    server_id: int
    server_label: str
    server_name: str | None
    server_hostid: str | None
    server_port: str | None
    daemon_name: str | None
    daemon_path: str | None
    options_path: str | None
    source_path: str | None
    raw_header: str | None
    last_parsed_at: datetime


class StaticLicenseGrantSummary(BaseModel):
    id: int
    server_id: int
    server_label: str
    license_file_asset_id: int | None
    feature_name: str
    vendor_name: str | None
    record_type: str
    version: str | None
    quantity: int | None
    issued_date: date | None
    start_date: date | None
    expiry_date: date | None
    expiry_text: str | None
    serial_number: str | None
    notice: str | None


class LicenseLogEventSummary(BaseModel):
    id: int
    server_id: int
    server_label: str
    event_type: str
    event_time: datetime | None
    vendor_daemon: str | None
    feature_name: str | None
    username: str | None
    hostname: str | None
    display: str | None
    raw_line: str


class FeatureUsageAggregateSummary(BaseModel):
    feature_name: str
    vendor: str
    server_names: list[str]
    current_users: list[str]
    current_checkout_count: int
    log_users: list[str]
    unique_user_count: int
    total_log_events: int
    checkout_events: int
    checkin_events: int
    denied_events: int
    last_seen: datetime | None


class UserUsageRankingSummary(BaseModel):
    username: str
    server_names: list[str]
    feature_names: list[str]
    unique_feature_count: int
    current_checkout_count: int
    total_log_events: int
    checkout_events: int
    checkin_events: int
    denied_events: int
    last_seen: datetime | None


class LicenseKeySummary(BaseModel):
    id: int
    key_name: str
    vendor: str
    version: str | None
    server_name: str
    issued: int
    used: int
    available: int
    usage_percent: float


class LicenseUsageSummary(BaseModel):
    id: int
    key_name: str
    vendor: str
    version: str | None
    username: str
    client_hostname: str
    last_used: str
    server_name: str
