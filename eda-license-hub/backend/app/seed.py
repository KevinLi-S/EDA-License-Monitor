from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.entities import Alert, Feature, FeatureSnapshot, LicenseServer, Vendor


def seed_if_empty(db: Session):
    if db.query(Vendor).count() > 0:
        return

    vendors = [Vendor(name=n) for n in ["synopsys", "cadence", "mentor", "ansys"]]
    db.add_all(vendors)
    db.flush()

    servers = [
        LicenseServer(vendor_id=vendors[0].id, name="snps-lic-01", host="10.0.0.11", port=27000, status="online", last_seen_at=datetime.utcnow()),
        LicenseServer(vendor_id=vendors[1].id, name="cdns-lic-01", host="10.0.0.12", port=5280, status="online", last_seen_at=datetime.utcnow()),
    ]
    db.add_all(servers)
    db.flush()

    feats = [
        Feature(vendor_id=vendors[0].id, name="VCS"),
        Feature(vendor_id=vendors[0].id, name="DC"),
        Feature(vendor_id=vendors[1].id, name="Virtuoso"),
    ]
    db.add_all(feats)
    db.flush()

    now = datetime.utcnow()
    points = [
        FeatureSnapshot(server_id=servers[0].id, feature_id=feats[0].id, total=100, used=76, free=24, collected_at=now - timedelta(minutes=5)),
        FeatureSnapshot(server_id=servers[0].id, feature_id=feats[1].id, total=40, used=35, free=5, collected_at=now - timedelta(minutes=5)),
        FeatureSnapshot(server_id=servers[1].id, feature_id=feats[2].id, total=60, used=22, free=38, collected_at=now - timedelta(minutes=5)),
    ]
    db.add_all(points)

    db.add(Alert(type="low_free", severity="high", server_id=servers[0].id, feature_id=feats[1].id, message="DC free licenses < 10", status="open"))
    db.commit()
