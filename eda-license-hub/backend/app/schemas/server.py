from pydantic import BaseModel


class ServerSummary(BaseModel):
    id: int
    name: str
    vendor: str
    host: str
    port: int
    status: str
    feature_count: int
    usage_percent: float
