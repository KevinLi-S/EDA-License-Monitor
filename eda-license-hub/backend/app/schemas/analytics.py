from datetime import datetime

from pydantic import BaseModel


class UsageTrendPoint(BaseModel):
    timestamp: datetime
    usage_percent: float
