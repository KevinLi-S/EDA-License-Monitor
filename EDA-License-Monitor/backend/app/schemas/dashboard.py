from pydantic import BaseModel

from app.schemas.alert import AlertSummary
from app.schemas.server import ServerSummary


class DashboardKpi(BaseModel):
    label: str
    value: str
    trend: str


class DashboardOverview(BaseModel):
    kpis: list[DashboardKpi]
    servers: list[ServerSummary]
    alerts: list[AlertSummary]
