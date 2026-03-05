from datetime import datetime
from pydantic import BaseModel


class FeaturePoint(BaseModel):
    feature: str
    total: int
    used: int
    free: int
    server: str
    vendor: str
    collected_at: datetime


class DashboardSummary(BaseModel):
    vendor_count: int
    server_count: int
    open_alerts: int
    top_busy_features: list[FeaturePoint]


class ServerActionRequest(BaseModel):
    action: str
