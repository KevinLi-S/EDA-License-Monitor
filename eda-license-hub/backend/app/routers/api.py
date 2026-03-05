from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.entities import Alert, Feature, FeatureSnapshot, LicenseServer, ServerActionLog, Vendor
from app.schemas import DashboardSummary, FeaturePoint, ServerActionRequest, ServerUpsertRequest

router = APIRouter(prefix="/api", tags=["api"])


def build_vendor_command(vendor: str, host: str, port: int, action: str) -> str:
    vendor = vendor.lower()
    if vendor == "synopsys":
        return f"snpslmdctl {action} --server {host}:{port}"
    if vendor == "cadence":
        return f"cdslmdctl {action} --server {host}:{port}"
    if vendor == "mentor":
        return f"mgcldctl {action} --server {host}:{port}"
    if vendor == "ansys":
        return f"anslic_admin -{action} {host}:{port}"
    return f"licensectl --vendor {vendor} {action} --server {host}:{port}"


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


@router.post("/servers")
def create_server(req: ServerUpsertRequest, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(func.lower(Vendor.name) == req.vendor.lower()).first()
    if not vendor:
        vendor = Vendor(name=req.vendor.lower())
        db.add(vendor)
        db.flush()

    server = LicenseServer(
        vendor_id=vendor.id,
        name=req.name,
        host=req.host,
        port=req.port,
        status="offline",
        last_seen_at=datetime.utcnow(),
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return {"ok": True, "id": server.id}


@router.put("/servers/{server_id}")
def update_server(server_id: int, req: ServerUpsertRequest, db: Session = Depends(get_db)):
    server = db.query(LicenseServer).filter(LicenseServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="server not found")

    vendor = db.query(Vendor).filter(func.lower(Vendor.name) == req.vendor.lower()).first()
    if not vendor:
        vendor = Vendor(name=req.vendor.lower())
        db.add(vendor)
        db.flush()

    server.name = req.name
    server.vendor_id = vendor.id
    server.host = req.host
    server.port = req.port
    db.add(server)
    db.commit()
    return {"ok": True}


@router.delete("/servers/{server_id}")
def delete_server(server_id: int, db: Session = Depends(get_db)):
    server = db.query(LicenseServer).filter(LicenseServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="server not found")
    db.delete(server)
    db.commit()
    return {"ok": True}


@router.get("/servers/{server_id}/action-preview")
def server_action_preview(server_id: int, action: str, db: Session = Depends(get_db)):
    server_vendor = (
        db.query(LicenseServer, Vendor.name)
        .join(Vendor, Vendor.id == LicenseServer.vendor_id)
        .filter(LicenseServer.id == server_id)
        .first()
    )
    if not server_vendor:
        raise HTTPException(status_code=404, detail="server not found")

    server, vendor_name = server_vendor
    action = action.lower().strip()
    if action not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=400, detail="action must be start|stop|restart")

    cmd = build_vendor_command(vendor_name, server.host, server.port, action)
    return {"server_id": server_id, "vendor": vendor_name, "action": action, "command": cmd}


@router.post("/servers/{server_id}/action")
def server_action(server_id: int, req: ServerActionRequest, db: Session = Depends(get_db)):
    server_vendor = (
        db.query(LicenseServer, Vendor.name)
        .join(Vendor, Vendor.id == LicenseServer.vendor_id)
        .filter(LicenseServer.id == server_id)
        .first()
    )
    if not server_vendor:
        raise HTTPException(status_code=404, detail="server not found")

    server, vendor_name = server_vendor
    action = req.action.lower().strip()
    if action not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=400, detail="action must be start|stop|restart")

    cmd = build_vendor_command(vendor_name, server.host, server.port, action)
    if req.dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "server_id": server_id,
            "action": action,
            "status": server.status,
            "command": cmd,
            "message": "Dry run only. No real execution.",
        }

    if action == "start":
        server.status = "online"
        msg = "service started"
    elif action == "stop":
        server.status = "offline"
        msg = "service stopped"
    else:
        server.status = "restarting"
        msg = "service restarting"

    server.last_seen_at = datetime.utcnow()
    db.add(server)
    db.flush()

    db.add(ServerActionLog(server_id=server.id, action=action, status_after=server.status, message=f"{msg}; cmd={cmd}"))
    db.commit()

    return {"ok": True, "dry_run": False, "server_id": server_id, "action": action, "status": server.status, "command": cmd}


@router.get("/server-actions")
def server_actions(db: Session = Depends(get_db)):
    rows = (
        db.query(ServerActionLog, LicenseServer.name)
        .join(LicenseServer, LicenseServer.id == ServerActionLog.server_id)
        .order_by(desc(ServerActionLog.created_at))
        .limit(100)
        .all()
    )
    return [
        {
            "id": log.id,
            "server": server_name,
            "action": log.action,
            "status_after": log.status_after,
            "message": log.message,
            "created_at": log.created_at,
        }
        for log, server_name in rows
    ]


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
