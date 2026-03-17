from fastapi import APIRouter

from app.api.routes import alerts, analytics, health, licenses, overview, servers

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(overview.router, tags=["overview"])
api_router.include_router(servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(licenses.router, prefix="/licenses", tags=["licenses"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
