from pydantic import BaseModel


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
