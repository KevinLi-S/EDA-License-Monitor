from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.entities import Alert, Feature, FeatureSnapshot, LicenseServer, Vendor
from app.schemas import DashboardSummary, FeaturePoint, ServerActionRequest

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)):
    top_rows = (
        db.query(
            Feature.name,
            FeatureSnapshot.total,
            FeatureSnapshot.used,
            FeatureSnapshot.free,
            LicenseServer.name,
            Vendor.name,
            FeatureSnapshot.collected_at,
        )
        .join(Feature, Feature.id == FeatureSnapshot.feature_id)
        .join(LicenseServer, LicenseServer.id == FeatureSnapshot.server_id)
        .join(Vendor, Vendor.id == Feature.vendor_id)
        .order_by(desc(FeatureSnapshot.used))
        .limit(10)
        .all()
    )

    top_busy = [
        FeaturePoint(
            feature=r[0],
            total=r[1],
            used=r[2],
            free=r[3],
            server=r[4],
            vendor=r[5],
            collected_at=r[6],
        )
        for r in top_rows
    ]

    return DashboardSummary(
        vendor_count=db.query(func.count(Vendor.id)).scalar() or 0,
        server_count=db.query(func.count(LicenseServer.id)).scalar() or 0,
        open_alerts=db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar() or 0,
        top_busy_features=top_busy,
    )


@router.get("/servers")
def servers(db: Session = Depends(get_db)):
    rows = db.query(LicenseServer, Vendor.name).join(Vendor, Vendor.id == LicenseServer.vendor_id).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "vendor": v,
            "host": s.host,
            "port": s.port,
            "status": s.status,
            "last_seen_at": s.last_seen_at,
        }
        for s, v in rows
    ]


@router.post("/servers/{server_id}/action")
def server_action(server_id: int, req: ServerActionRequest, db: Session = Depends(get_db)):
    server = db.query(LicenseServer).filter(LicenseServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="server not found")

    action = req.action.lower().strip()
    if action not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=400, detail="action must be start|stop|restart")

    if action == "start":
        server.status = "online"
    elif action == "stop":
        server.status = "offline"
    else:
        server.status = "degraded"

    db.add(server)
    db.commit()

    return {"ok": True, "server_id": server_id, "action": action, "status": server.status}


@router.get("/features")
def features(db: Session = Depends(get_db)):
    rows = (
        db.query(FeatureSnapshot, Feature.name, LicenseServer.name, Vendor.name)
        .join(Feature, Feature.id == FeatureSnapshot.feature_id)
        .join(LicenseServer, LicenseServer.id == FeatureSnapshot.server_id)
        .join(Vendor, Vendor.id == Feature.vendor_id)
        .order_by(desc(FeatureSnapshot.collected_at))
        .all()
    )
    return [
        {
            "feature": f_name,
            "server": s_name,
            "vendor": v_name,
            "total": snap.total,
            "used": snap.used,
            "free": snap.free,
            "collected_at": snap.collected_at,
        }
        for snap, f_name, s_name, v_name in rows
    ]


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(desc(Alert.created_at)).all()
    return [
        {
            "id": a.id,
            "type": a.type,
            "severity": a.severity,
            "message": a.message,
            "status": a.status,
            "created_at": a.created_at,
        }
        for a in rows
    ]
