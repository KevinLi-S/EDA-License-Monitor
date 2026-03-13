from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import os
import re
import subprocess

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.entities import Alert, Feature, FeatureSnapshot, LicenseKeyRecord, LicenseServer, ServerActionLog, Vendor
from app.schemas import DashboardSummary, FeaturePoint, RiskSummary, RiskFinding, ServerActionRequest, ServerUpsertRequest

router = APIRouter(prefix="/api", tags=["api"])

# 配置常量
COMMAND_TIMEOUT = 20  # 秒
MAX_STDOUT_LENGTH = 120
MAX_STDERR_LENGTH = 180
MAX_LICENSE_KEYS_LIMIT = 1000
MAX_LOGS_LIMIT = 5000


def server_display_name(vendor: str, server_name: str) -> str:
    vendor = (vendor or '').strip().lower()
    server_name = (server_name or 'unknown').strip()
    return f"{server_name} ({vendor})" if vendor else server_name


def build_vendor_command(vendor: str, host: str, port: int, action: str) -> List[str]:
    """构建 vendor 命令参数列表，防止命令注入"""
    vendor = vendor.lower()
    server_addr = f"{host}:{port}"

    if vendor == "synopsys":
        return ["snpslmdctl", action, "--server", server_addr]
    if vendor == "cadence":
        return ["cdslmdctl", action, "--server", server_addr]
    if vendor == "mentor":
        return ["mgcldctl", action, "--server", server_addr]
    if vendor == "ansys":
        return ["anslic_admin", f"-{action}", server_addr]
    return ["licensectl", "--vendor", vendor, action, "--server", server_addr]


def build_vendor_command_str(vendor: str, host: str, port: int, action: str) -> str:
    """仅用于预览，返回命令字符串"""
    import shlex
    cmd_list = build_vendor_command(vendor, host, port, action)
    return " ".join(shlex.quote(arg) for arg in cmd_list)


def log_base_dir() -> Path:
    """获取日志基础目录，必须通过环境变量 LOG_BASE_DIR 配置"""
    p = os.getenv("LOG_BASE_DIR", "").strip()
    if not p:
        raise HTTPException(
            status_code=500,
            detail="LOG_BASE_DIR environment variable not configured. Please set it to your log directory path."
        )
    log_path = Path(p)
    if not log_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"LOG_BASE_DIR path does not exist: {log_path}"
        )
    return log_path


def iter_vendor_logs(vendor: str) -> List[Path]:
    base = log_base_dir()
    files = []
    exact = base / f"{vendor}.log"
    if exact.exists():
        files.append(exact)
    files.extend(sorted(base.glob(f"{vendor}_*.log")))
    return files


def parse_log_findings(vendor: str, path: Path) -> List[RiskFinding]:
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8", errors="replace")
    findings: List[RiskFinding] = []

    checks = [
        ("tampered", "critical", "License integrity warning detected", "CVD License file has been Tampered"),
        ("encrypted communication disabled", "high", "Ecomms disabled", "Encrypted Communication disabled"),
        ("external filters are off", "high", "External filters disabled", "EXTERNAL FILTERS are OFF"),
        ("options file used: none", "medium", "No options file", "Options file used: None"),
    ]

    low_text = text.lower()
    for key, severity, issue, detail in checks:
        if key in low_text:
            findings.append(RiskFinding(vendor=vendor, severity=severity, issue=issue, detail=detail))

    return findings


def build_risk_summary() -> RiskSummary:
    findings = []
    for p in iter_vendor_logs("synopsys"):
        findings.extend(parse_log_findings("synopsys", p))
    for p in iter_vendor_logs("ansys"):
        findings.extend(parse_log_findings("ansys", p))

    critical = sum(1 for f in findings if f.severity == "critical")
    high = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")

    return RiskSummary(critical=critical, high=high, medium=medium, findings=findings)


def derive_synopsys_activity_from_log() -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    """Compute current in-use count and active users per feature from synopsys OUT/IN events."""
    files = iter_vendor_logs("synopsys")
    if not files:
        return {}, {}

    # Example lines:
    # 3:58:19 (snpslmd) OUT: "3D" user@host  [14]
    # 4:03:01 (snpslmd) IN:  "3D" user@host  [14]
    out_re = re.compile(r'OUT:\s+"([^"]+)"\s+([^\s]+)', re.IGNORECASE)
    in_re = re.compile(r'IN:\s+"([^"]+)"\s+([^\s]+)', re.IGNORECASE)

    active_by_feature: Dict[str, Dict[str, int]] = {}

    for p in files:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m_out = out_re.search(line)
            if m_out:
                feat = m_out.group(1).strip()
                user = m_out.group(2).strip()
                per_user = active_by_feature.setdefault(feat, {})
                per_user[user] = per_user.get(user, 0) + 1
                continue

            m_in = in_re.search(line)
            if m_in:
                feat = m_in.group(1).strip()
                user = m_in.group(2).strip()
                per_user = active_by_feature.setdefault(feat, {})
                if per_user.get(user, 0) > 0:
                    per_user[user] -= 1
                    if per_user[user] <= 0:
                        per_user.pop(user, None)

    used: Dict[str, int] = {}
    users: Dict[str, List[str]] = {}
    for feat, per_user in active_by_feature.items():
        used[feat] = sum(per_user.values())
        users[feat] = sorted(per_user.keys())

    return used, users


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)):
    key_rows = db.query(LicenseKeyRecord).order_by(desc(LicenseKeyRecord.used)).limit(10).all()

    if key_rows:
        top_busy = [
            FeaturePoint(
                feature=r.feature,
                total=r.total,
                used=r.used,
                free=max(r.total - r.used, 0),
                server=r.server,
                vendor=r.vendor,
                collected_at=r.collected_at,
            )
            for r in key_rows
        ]
    else:
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

    real_vendor_count = db.query(func.count(func.distinct(LicenseKeyRecord.vendor))).scalar() or 0
    real_server_count = (
        db.query(func.count(func.distinct(LicenseKeyRecord.vendor + '|' + LicenseKeyRecord.server))).scalar() or 0
    )

    return DashboardSummary(
        vendor_count=real_vendor_count or (db.query(func.count(Vendor.id)).scalar() or 0),
        server_count=real_server_count or (db.query(func.count(LicenseServer.id)).scalar() or 0),
        open_alerts=db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar() or 0,
        top_busy_features=top_busy,
        risk_summary=build_risk_summary(),
    )


@router.get("/servers")
def servers(db: Session = Depends(get_db)):
    rows = db.query(LicenseServer, Vendor.name).join(Vendor, Vendor.id == LicenseServer.vendor_id).all()
    server_stats = {
        (vendor_name.lower(), server_name): (feature_count or 0, total_licenses or 0, used_licenses or 0)
        for vendor_name, server_name, feature_count, total_licenses, used_licenses in (
            db.query(
                LicenseKeyRecord.vendor,
                LicenseKeyRecord.server,
                func.count(func.distinct(LicenseKeyRecord.feature)),
                func.coalesce(func.sum(LicenseKeyRecord.total), 0),
                func.coalesce(func.sum(LicenseKeyRecord.used), 0),
            )
            .group_by(LicenseKeyRecord.vendor, LicenseKeyRecord.server)
            .all()
        )
    }

    return [
        {
            "id": s.id,
            "name": s.name,
            "vendor": v,
            "host": s.host,
            "port": s.port,
            "status": s.status,
            "last_seen_at": s.last_seen_at,
            "feature_count": server_stats.get(((v or '').lower(), server_display_name(v, s.name)), (0, 0, 0))[0],
            "total_licenses": server_stats.get(((v or '').lower(), server_display_name(v, s.name)), (0, 0, 0))[1],
            "used_licenses": server_stats.get(((v or '').lower(), server_display_name(v, s.name)), (0, 0, 0))[2],
        }
        for s, v in rows
        if ((v or '').lower(), server_display_name(v, s.name)) in server_stats or not server_stats
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
        last_seen_at=datetime.now(timezone.utc),
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

    cmd = build_vendor_command_str(vendor_name, server.host, server.port, action)
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

    cmd_list = build_vendor_command(vendor_name, server.host, server.port, action)
    cmd_str = build_vendor_command_str(vendor_name, server.host, server.port, action)

    if req.dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "server_id": server_id,
            "action": action,
            "status": server.status,
            "command": cmd_str,
            "message": "Dry run only. No real execution.",
        }

    # Real execution mode: run command and only update status if command succeeds.
    try:
        res = subprocess.run(cmd_list, shell=False, capture_output=True, text=True, timeout=COMMAND_TIMEOUT)
        ok = res.returncode == 0
        stdout = (res.stdout or "").strip()
        stderr = (res.stderr or "").strip()
    except Exception as e:
        ok = False
        stdout = ""
        stderr = str(e)

    if ok:
        if action == "start":
            server.status = "online"
        elif action == "stop":
            server.status = "offline"
        else:
            server.status = "restarting"
        server.last_seen_at = datetime.utcnow()
        db.add(server)
        db.flush()

    db.add(
        ServerActionLog(
            server_id=server.id,
            action=action,
            status_after=server.status,
            message=f"cmd={cmd_str}; rc={(0 if ok else 1)}; out={stdout[:MAX_STDOUT_LENGTH]}; err={stderr[:MAX_STDERR_LENGTH]}",
        )
    )
    db.commit()

    return {
        "ok": ok,
        "dry_run": False,
        "server_id": server_id,
        "action": action,
        "status": server.status,
        "command": cmd_str,
        "stdout": stdout,
        "stderr": stderr,
    }


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


@router.post("/license/upload")
async def upload_license(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8", errors="replace")
    lines = [x.strip() for x in content.splitlines() if x.strip()]

    server_line = next((x for x in lines if x.upper().startswith("SERVER ")), "")
    daemon_line = next((x for x in lines if x.upper().startswith("DAEMON ")), "")
    vendor_line = next((x for x in lines if x.upper().startswith("VENDOR ")), "")

    server_name = "uploaded-lic-01"
    server_port = 27000
    if server_line:
        p = server_line.split()
        if len(p) >= 4:
            server_name = p[1]
            try:
                server_port = int(p[3])
            except Exception:
                pass

    vendor_name = "synopsys"
    daemon_or_vendor_line = daemon_line or vendor_line
    if daemon_or_vendor_line:
        p = daemon_or_vendor_line.split()
        daemon_token = (p[1].lower() if len(p) >= 2 else "")
        if "snpslmd" in daemon_token:
            vendor_name = "synopsys"
        elif "cdslmd" in daemon_token or "cds" in daemon_token:
            vendor_name = "cadence"
        elif "mgcld" in daemon_token or "mentor" in daemon_token or "saltd" in daemon_token:
            vendor_name = "mentor"
        elif "ansyslmd" in daemon_token or "ansys" in daemon_token:
            vendor_name = "ansys"

    fn = (file.filename or "").lower()
    if fn.startswith("cadence_"):
        vendor_name = "cadence"
    elif fn.startswith("mentor_"):
        vendor_name = "mentor"
    elif fn.startswith("synopsys_"):
        vendor_name = "synopsys"
    elif fn.startswith("ansys_"):
        vendor_name = "ansys"

    vendor = db.query(Vendor).filter(func.lower(Vendor.name) == vendor_name).first()
    if not vendor:
        vendor = Vendor(name=vendor_name)
        db.add(vendor)
        db.flush()

    server = (
        db.query(LicenseServer)
        .filter(LicenseServer.vendor_id == vendor.id, LicenseServer.name == server_name, LicenseServer.port == server_port)
        .first()
    )
    if not server:
        server = LicenseServer(
            vendor_id=vendor.id,
            name=server_name,
            host=server_name,
            port=server_port,
            status="online",
            last_seen_at=datetime.now(timezone.utc),
        )
        db.add(server)
        db.flush()

    # replace previous records from same source file
    db.query(LicenseKeyRecord).filter(LicenseKeyRecord.source_file == (file.filename or "")).delete()

    created = 0
    in_regex = re.compile(r"^INCREMENT\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", re.IGNORECASE)
    feat_regex = re.compile(r"^FEATURE\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", re.IGNORECASE)
    synopsys_used_map, _synopsys_users_map = derive_synopsys_activity_from_log() if vendor_name == "synopsys" else ({}, {})

    for line in lines:
        m = in_regex.match(line) or feat_regex.match(line)
        if not m:
            continue

        feat_name, daemon, version, expiry, total = m.groups()

        feature = db.query(Feature).filter(Feature.vendor_id == vendor.id, Feature.name == feat_name).first()
        if not feature:
            feature = Feature(vendor_id=vendor.id, name=feat_name)
            db.add(feature)
            db.flush()

        try:
            total_i = int(total)
        except Exception:
            total_i = 1

        if vendor_name == "synopsys":
            used = min(max(synopsys_used_map.get(feat_name, 0), 0), total_i)
        else:
            used = min(max(total_i // 2, 0), total_i)

        db.add(
            FeatureSnapshot(
                server_id=server.id,
                feature_id=feature.id,
                total=total_i,
                used=used,
                free=total_i - used,
                collected_at=datetime.now(timezone.utc),
            )
        )

        db.add(
            LicenseKeyRecord(
                vendor=vendor_name,
                feature=feat_name,
                version=version,
                total=total_i,
                used=used,
                expiry=expiry,
                server=server_display_name(vendor_name, server_name),
                source_file=file.filename or "",
                collected_at=datetime.now(timezone.utc),
            )
        )
        created += 1

    db.add(
        Alert(
            type="license_upload",
            severity="medium",
            server_id=server.id,
            feature_id=None,
            message=f"Uploaded {file.filename}, parsed {created} features",
            status="open",
        )
    )

    db.commit()
    return {"ok": True, "parsed_features": created, "filename": file.filename, "server": server_name, "port": server_port}


@router.get("/license-keys")
def license_keys(vendor: str = "all", keyword: str = "", limit: int = 500, db: Session = Depends(get_db)):
    # 验证并限制 limit 参数
    limit = max(1, min(limit, MAX_LICENSE_KEYS_LIMIT))

    syn_used, syn_users = derive_synopsys_activity_from_log()

    q = db.query(LicenseKeyRecord)
    if vendor != "all":
        q = q.filter(func.lower(LicenseKeyRecord.vendor) == vendor.lower())
    if keyword.strip():
        kw = f"%{keyword.strip()}%"
        q = q.filter(LicenseKeyRecord.feature.ilike(kw))

    records = q.order_by(desc(LicenseKeyRecord.collected_at)).limit(max(1, min(limit, 5000))).all()
    if records:
        out = []
        for r in records:
            users = syn_users.get(r.feature, []) if (r.vendor or '').lower() == 'synopsys' else []
            used_now = syn_used.get(r.feature, r.used) if (r.vendor or '').lower() == 'synopsys' else r.used
            out.append(
                {
                    "id": r.id,
                    "feature": r.feature,
                    "vendor": r.vendor,
                    "version": r.version,
                    "total": r.total,
                    "used": min(max(used_now, 0), r.total),
                    "expiry": r.expiry,
                    "server": r.server,
                    "active_user_count": len(users),
                    "active_users": users,
                }
            )
        return out

    rows = (
        db.query(FeatureSnapshot, Feature.name, LicenseServer.name, Vendor.name)
        .join(Feature, Feature.id == FeatureSnapshot.feature_id)
        .join(LicenseServer, LicenseServer.id == FeatureSnapshot.server_id)
        .join(Vendor, Vendor.id == Feature.vendor_id)
        .order_by(desc(FeatureSnapshot.collected_at))
        .limit(200)
        .all()
    )

    return [
        {
            "id": idx,
            "feature": f_name,
            "vendor": (v_name or "").lower(),
            "version": "N/A",
            "total": snap.total,
            "used": snap.used,
            "expiry": "N/A",
            "server": s_name,
            "active_user_count": 0,
            "active_users": [],
        }
        for idx, (snap, f_name, s_name, v_name) in enumerate(rows, start=1)
    ]


@router.get("/license-logs")
def license_logs(vendor: str = "all", keyword: str = "", mode: str = "full", limit: int = 1000):
    # 验证并限制 limit 参数
    limit = max(1, min(limit, MAX_LOGS_LIMIT))
    files = []
    if vendor in {"all", "synopsys"}:
        files.extend([("synopsys", p) for p in iter_vendor_logs("synopsys")])
    if vendor in {"all", "ansys"}:
        files.extend([("ansys", p) for p in iter_vendor_logs("ansys")])
    if vendor in {"all", "cadence"}:
        files.extend([("cadence", p) for p in iter_vendor_logs("cadence")])
    if vendor in {"all", "mentor"}:
        files.extend([("mentor", p) for p in iter_vendor_logs("mentor")])

    patterns = ["error", "denied", "failed", "tampered", "unsupported", "cannot", "refused", "expired"]
    keyword = (keyword or "").strip().lower()
    mode = (mode or "full").lower()

    out = []
    for v, p in files:
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines, start=1):
            low = line.lower()
            match_error = any(k in low for k in patterns)
            if mode == "error" and not match_error:
                continue
            if keyword and keyword not in low:
                continue
            out.append({"id": f"{v}-{i}", "vendor": v, "line": i, "content": line.rstrip()})

    return out[-limit:]

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
