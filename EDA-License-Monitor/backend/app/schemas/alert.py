from datetime import datetime

from pydantic import BaseModel


class AlertSummary(BaseModel):
    id: int
    severity: str
    message: str
    triggered_at: datetime
    source: str
