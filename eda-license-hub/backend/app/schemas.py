from datetime import datetime
from typing import List
from pydantic import BaseModel


class FeaturePoint(BaseModel):
    feature: str
    total: int
    used: int
    free: int
    server: str
    vendor: str
    collected_at: datetime


class RiskFinding(BaseModel):
    vendor: str
    severity: str
    issue: str
    detail: str


class RiskSummary(BaseModel):
    critical: int
    high: int
    medium: int
    findings: List[RiskFinding]


class DashboardSummary(BaseModel):
    vendor_count: int
    server_count: int
    open_alerts: int
    top_busy_features: List[FeaturePoint]
    risk_summary: RiskSummary


class ServerActionRequest(BaseModel):
    action: str
    dry_run: bool = True


class ServerUpsertRequest(BaseModel):
    name: str
    vendor: str
    host: str
    port: int
