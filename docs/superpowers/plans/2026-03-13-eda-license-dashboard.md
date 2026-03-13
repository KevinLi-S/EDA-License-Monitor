# EDA License Dashboard Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an enterprise-grade EDA license monitoring and management platform with real-time updates, alerts, and centralized control.

**Architecture:** Microservices architecture with FastAPI backend, React frontend, PostgreSQL for persistence, Redis for caching/messaging, Celery for async tasks, and WebSocket for real-time updates. Docker-compose deployment.

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Celery, Paramiko
- Frontend: React 18, TypeScript, Ant Design Pro, Recharts
- Data: PostgreSQL 15, Redis 7
- Deployment: Docker, Docker Compose, Nginx

---

## Project Structure

```
eda-license-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # Database connection
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── server.py
│   │   │   ├── feature.py
│   │   │   ├── usage.py
│   │   │   ├── alert.py
│   │   │   └── user.py
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── server.py
│   │   │   ├── feature.py
│   │   │   └── auth.py
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── servers.py
│   │   │   ├── features.py
│   │   │   ├── alerts.py
│   │   │   └── websocket.py
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── license_collector.py
│   │   │   ├── lmstat_parser.py
│   │   │   ├── alert_engine.py
│   │   │   ├── server_manager.py
│   │   │   └── analytics.py
│   │   ├── tasks/                  # Celery tasks
│   │   │   ├── __init__.py
│   │   │   └── collector.py
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── websocket_manager.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_parser.py
│   │   ├── test_collector.py
│   │   ├── test_api.py
│   │   └── test_alerts.py
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── celery_app.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── ServerCard.tsx
│   │   │   │   ├── FeatureCard.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   └── UsageTable.tsx
│   │   │   ├── Management/
│   │   │   │   ├── ServerControl.tsx
│   │   │   │   ├── AlertConfig.tsx
│   │   │   │   └── LogViewer.tsx
│   │   │   └── Common/
│   │   │       ├── Loading.tsx
│   │   │       └── ErrorBoundary.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ServerDetail.tsx
│   │   │   ├── Management.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Login.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── auth.ts
│   │   ├── store/
│   │   │   ├── serverSlice.ts
│   │   │   ├── featureSlice.ts
│   │   │   └── authSlice.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-03-13-eda-license-dashboard-design.md
│       └── plans/
│           └── 2026-03-13-eda-license-dashboard.md
└── README.md
```

---

## Chunk 1: Foundation - Project Setup & Database

**Goal:** Set up project structure, database schema, and core models. Result: Working database with schemas, can insert/query test data.

### Task 1.1: Initialize Backend Project Structure

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/.env.example`
- Create: `.gitignore`

**Prerequisites:** PostgreSQL 15+ and Python 3.11+ installed and accessible.

- [ ] **Step 1: Initialize git repository**

```bash
cd /c/Users/李文瑞/Desktop/eda-license-dashboard
git init
```

Expected: "Initialized empty Git repository..."

- [ ] **Step 2: Create .gitignore**

```txt
# .gitignore
.superpowers/
*.pyc
__pycache__/
.env
.venv/
venv/
node_modules/
.DS_Store
*.log
.idea/
.vscode/
*.swp
*.egg-info/
dist/
build/
.pytest_cache/
```

- [ ] **Step 3: Create backend directory structure**

```bash
mkdir -p backend/app backend/tests backend/scripts
cd backend
touch requirements.txt
```

Expected: Directories and file created

- [ ] **Step 4: Add dependencies to requirements.txt**

```txt
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
celery==5.3.4
redis==5.0.1
paramiko==3.3.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

- [ ] **Step 5: Create config.py with settings**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://eda_admin:password@localhost:5432/eda_license"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 2

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Collection
    COLLECTION_INTERVAL_SECONDS: int = 30
    LMSTAT_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 6: Create .env.example**

```bash
# backend/.env.example
DATABASE_URL=postgresql://eda_admin:password@postgres:5432/eda_license
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change-me-in-production
CORS_ORIGINS=http://localhost:3000
```

- [ ] **Step 7: Initialize app package**

```python
# backend/app/__init__.py
"""EDA License Dashboard Backend"""

__version__ = "0.1.0"
```

- [ ] **Step 8: Commit initial structure**

```bash
git add .gitignore backend/
git commit -m "feat: initialize backend project structure

Add:
- .gitignore for Python/Node artifacts
- requirements.txt with core dependencies
- config.py with pydantic-settings
- .env.example for configuration
- Basic project structure

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

Expected: Files committed successfully

### Task 1.2: Set Up Database Connection

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_database.py`

**Prerequisites:** PostgreSQL 15+ installed and running.

- [ ] **Step 1: Create PostgreSQL user and set password**

```bash
# Connect as postgres superuser
sudo -u postgres psql

# In psql, run:
CREATE USER eda_admin WITH PASSWORD 'password';
ALTER USER eda_admin CREATEDB;
\q
```

Expected: "CREATE ROLE" and "ALTER ROLE"

Note: In production, use a strong password and store it in .env file. The password 'password' is for development only.

- [ ] **Step 2: Write test for database connection**

```python
# backend/tests/test_database.py
import pytest
from sqlalchemy import text
from app.database import get_db, engine


def test_database_connection():
    """Test that we can connect to the database"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_get_db_session():
    """Test that get_db returns a working session"""
    db = next(get_db())
    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        db.close()
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd backend
pytest tests/test_database.py -v
```

Expected: FAIL - ImportError or ModuleNotFoundError for app.database

- [ ] **Step 4: Implement database.py**

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Create conftest.py for shared fixtures**

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings

# Use test database
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/eda_license", "/eda_license_test")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 6: Create PostgreSQL databases**

```bash
# Create main database and test database
psql -U eda_admin -c "CREATE DATABASE eda_license;"
psql -U eda_admin -c "CREATE DATABASE eda_license_test;"
```

Expected: "CREATE DATABASE" for both

Note: If you get "database already exists" error, that's OK - skip to next step.

- [ ] **Step 7: Run tests to verify they pass**

```bash
cd backend
pytest tests/test_database.py -v
```

Expected: 2/2 tests PASS

- [ ] **Step 8: Commit**

```bash
git add app/database.py tests/conftest.py tests/test_database.py
git commit -m "feat: add database connection and session management

Add:
- database.py with SQLAlchemy engine and session factory
- get_db dependency for FastAPI
- Test fixtures in conftest.py
- Tests for database connection

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.3: Create Database Models - License Servers

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/server.py`
- Create: `backend/tests/test_models_server.py`

- [ ] **Step 1: Write test for LicenseServer model**

```python
# backend/tests/test_models_server.py
import pytest
from datetime import datetime
from app.models.server import LicenseServer


def test_create_license_server(db_session):
    """Test creating a license server"""
    server = LicenseServer(
        name="Synopsys Main",
        vendor="synopsys",
        host="license-syn-01.eda.local",
        port=27000,
        lmutil_path="/opt/synopsys/lmutil",
        ssh_host="license-syn-01.eda.local",
        ssh_port=22,
        ssh_user="admin",
        status="active"
    )

    db_session.add(server)
    db_session.commit()

    assert server.id is not None
    assert server.name == "Synopsys Main"
    assert server.vendor == "synopsys"
    assert server.created_at is not None


def test_license_server_relationships(db_session):
    """Test that server can have features"""
    server = LicenseServer(
        name="Test Server",
        vendor="synopsys",
        host="test.local",
        port=27000
    )

    db_session.add(server)
    db_session.commit()

    # Should have empty features list initially
    assert server.features == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models_server.py -v
```

Expected: FAIL - ImportError for app.models.server

- [ ] **Step 3: Implement LicenseServer model**

```python
# backend/app/models/__init__.py
from app.database import Base
from app.models.server import LicenseServer

__all__ = ["Base", "LicenseServer"]
```

```python
# backend/app/models/server.py
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
from sqlalchemy.orm import relationship


class LicenseServer(Base):
    """License server configuration"""
    __tablename__ = "license_servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    vendor = Column(String(50), nullable=False, index=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False, default=27000)
    lmutil_path = Column(String(255))
    ssh_host = Column(String(255))
    ssh_port = Column(Integer, default=22)
    ssh_user = Column(String(50))
    ssh_key_path = Column(String(255))
    status = Column(String(20), default='active', index=True)
    last_check_time = Column(DateTime)
    last_status = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships (will be populated when Feature model is created)
    features = relationship("LicenseFeature", back_populates="server", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LicenseServer(id={self.id}, name='{self.name}', vendor='{self.vendor}')>"
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_models_server.py -v
```

Expected: test_create_license_server will PASS. test_license_server_relationships will FAIL with an error about LicenseFeature not being defined - this is expected since we're using a forward reference to a model that doesn't exist yet.

Note: The relationship to LicenseFeature uses a string reference ("LicenseFeature"), which SQLAlchemy will attempt to resolve when the model is imported. Since it doesn't exist yet, this test will fail. This is temporary and expected - the test will pass once LicenseFeature is created in Task 1.4.

- [ ] **Step 5: Commit**

```bash
git add app/models/ tests/test_models_server.py
git commit -m "feat: add LicenseServer model

Add:
- LicenseServer SQLAlchemy model
- Tests for server creation and relationships
- Model includes vendor, host, port, SSH config
- Forward reference to LicenseFeature (will be created next)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.4: Create Database Models - License Features

**Files:**
- Create: `backend/app/models/feature.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_models_feature.py`

- [ ] **Step 1: Write test for LicenseFeature model**

```python
# backend/tests/test_models_feature.py
import pytest
from datetime import date
from app.models.server import LicenseServer
from app.models.feature import LicenseFeature


def test_create_license_feature(db_session):
    """Test creating a license feature"""
    # Create server first
    server = LicenseServer(
        name="Test Server",
        vendor="synopsys",
        host="test.local",
        port=27000
    )
    db_session.add(server)
    db_session.commit()

    # Create feature
    feature = LicenseFeature(
        server_id=server.id,
        feature_name="VCS_Runtime",
        total_licenses=200,
        vendor="synopsys",
        version="2023.12",
        expiry_date=date(2025, 12, 31)
    )

    db_session.add(feature)
    db_session.commit()

    assert feature.id is not None
    assert feature.feature_name == "VCS_Runtime"
    assert feature.total_licenses == 200
    assert feature.server.name == "Test Server"


def test_feature_server_relationship(db_session):
    """Test bidirectional relationship between server and features"""
    server = LicenseServer(
        name="Test Server",
        vendor="synopsys",
        host="test.local",
        port=27000
    )
    db_session.add(server)
    db_session.commit()

    feature1 = LicenseFeature(
        server_id=server.id,
        feature_name="VCS_Runtime",
        total_licenses=200
    )
    feature2 = LicenseFeature(
        server_id=server.id,
        feature_name="DC_Ultra",
        total_licenses=12
    )

    db_session.add_all([feature1, feature2])
    db_session.commit()

    # Refresh to get relationships
    db_session.refresh(server)

    assert len(server.features) == 2
    assert feature1.server.name == "Test Server"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models_feature.py -v
```

Expected: FAIL - ImportError for app.models.feature

- [ ] **Step 3: Implement LicenseFeature model**

```python
# backend/app/models/feature.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class LicenseFeature(Base):
    """License feature/product"""
    __tablename__ = "license_features"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("license_servers.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(100), nullable=False)
    total_licenses = Column(Integer, nullable=False)
    vendor = Column(String(50))
    version = Column(String(50))
    expiry_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    server = relationship("LicenseServer", back_populates="features")
    usage_history = relationship("LicenseUsageHistory", back_populates="feature", cascade="all, delete-orphan")
    checkouts = relationship("LicenseCheckout", back_populates="feature", cascade="all, delete-orphan")

    # Unique constraint on server_id + feature_name
    __table_args__ = (
        UniqueConstraint('server_id', 'feature_name', name='uix_server_feature'),
    )

    def __repr__(self):
        return f"<LicenseFeature(id={self.id}, name='{self.feature_name}', total={self.total_licenses})>"
```

- [ ] **Step 4: Add LicenseFeature import to models/__init__.py**

Modify `backend/app/models/__init__.py` to import the new LicenseFeature model:

```python
# backend/app/models/__init__.py
from app.database import Base
from app.models.server import LicenseServer
from app.models.feature import LicenseFeature

__all__ = ["Base", "LicenseServer", "LicenseFeature"]
```

- [ ] **Step 5: Run all model tests to verify relationships are complete**

```bash
cd backend
pytest tests/test_models_server.py tests/test_models_feature.py -v
```

Expected: ALL tests PASS, including:
- test_create_license_server ✓
- test_license_server_relationships ✓ (now passes because LicenseFeature exists)
- test_create_license_feature ✓
- test_feature_server_relationship ✓

Note: This verifies that the forward reference from Task 1.3 is now resolved. The LicenseServer -> LicenseFeature relationship that was failing before should now work correctly.

- [ ] **Step 6: Commit**

```bash
git add app/models/feature.py app/models/__init__.py tests/test_models_feature.py tests/test_models_server.py
git commit -m "feat: add LicenseFeature model with server relationship

Add:
- LicenseFeature model with vendor, version, expiry
- Bidirectional relationship with LicenseServer
- Unique constraint on server_id + feature_name
- Tests for feature creation and relationships

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.5: Create Database Models - Usage History & Checkouts

**Files:**
- Create: `backend/app/models/usage.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/models/feature.py` (uncomment relationships)
- Create: `backend/tests/test_models_usage.py`

- [ ] **Step 1: Write tests for usage models**

```python
# backend/tests/test_models_usage.py
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.server import LicenseServer
from app.models.feature import LicenseFeature
from app.models.usage import LicenseUsageHistory, LicenseCheckout


def test_create_usage_history(db_session):
    """Test creating usage history record"""
    # Setup server and feature
    server = LicenseServer(name="Test", vendor="synopsys", host="test.local", port=27000)
    db_session.add(server)
    db_session.commit()

    feature = LicenseFeature(server_id=server.id, feature_name="VCS", total_licenses=200)
    db_session.add(feature)
    db_session.commit()

    # Create usage record
    usage = LicenseUsageHistory(
        feature_id=feature.id,
        timestamp=datetime.now(),
        used_count=156,
        available_count=44,
        usage_percentage=Decimal("78.00"),
        queued_count=0
    )

    db_session.add(usage)
    db_session.commit()

    assert usage.id is not None
    assert usage.used_count == 156
    assert usage.usage_percentage == Decimal("78.00")
    assert usage.feature.feature_name == "VCS"


def test_create_checkout(db_session):
    """Test creating checkout record"""
    # Setup
    server = LicenseServer(name="Test", vendor="synopsys", host="test.local", port=27000)
    db_session.add(server)
    db_session.commit()

    feature = LicenseFeature(server_id=server.id, feature_name="VCS", total_licenses=200)
    db_session.add(feature)
    db_session.commit()

    # Create checkout
    checkout = LicenseCheckout(
        feature_id=feature.id,
        username="zhang.wei",
        hostname="server-01.eda.local",
        display=":0",
        process_info="vcs (PID: 12345)",
        checkout_time=datetime.now(),
        server_handle="12345",
        is_active=True
    )

    db_session.add(checkout)
    db_session.commit()

    assert checkout.id is not None
    assert checkout.username == "zhang.wei"
    assert checkout.is_active is True
    assert checkout.feature.feature_name == "VCS"


def test_checkout_cascade_delete(db_session):
    """Test that checkouts are deleted when feature is deleted"""
    server = LicenseServer(name="Test", vendor="synopsys", host="test.local", port=27000)
    db_session.add(server)
    db_session.commit()

    feature = LicenseFeature(server_id=server.id, feature_name="VCS", total_licenses=200)
    db_session.add(feature)
    db_session.commit()

    checkout = LicenseCheckout(
        feature_id=feature.id,
        username="test.user",
        hostname="test.host",
        checkout_time=datetime.now()
    )
    db_session.add(checkout)
    db_session.commit()

    feature_id = feature.id
    checkout_id = checkout.id

    # Delete feature
    db_session.delete(feature)
    db_session.commit()

    # Checkout should be deleted
    deleted_checkout = db_session.query(LicenseCheckout).filter_by(id=checkout_id).first()
    assert deleted_checkout is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_models_usage.py -v
```

Expected: FAIL - ImportError

- [ ] **Step 3: Implement usage models**

```python
# backend/app/models/usage.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, DECIMAL, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base


class LicenseUsageHistory(Base):
    """Historical license usage data"""
    __tablename__ = "license_usage_history"

    id = Column(BigInteger, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("license_features.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    used_count = Column(Integer, nullable=False)
    available_count = Column(Integer, nullable=False)
    usage_percentage = Column(DECIMAL(5, 2))
    queued_count = Column(Integer, default=0)

    # Relationship
    feature = relationship("LicenseFeature", back_populates="usage_history")

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_feature_timestamp', 'feature_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<LicenseUsageHistory(feature_id={self.feature_id}, used={self.used_count}/{self.used_count + self.available_count})>"


class LicenseCheckout(Base):
    """Current license checkout/occupancy records"""
    __tablename__ = "license_checkouts"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("license_features.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(100), nullable=False, index=True)
    hostname = Column(String(255), nullable=False)
    display = Column(String(100))
    process_info = Column(String)
    checkout_time = Column(DateTime, nullable=False)
    server_handle = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    feature = relationship("LicenseFeature", back_populates="checkouts")

    # Index for active checkouts query
    __table_args__ = (
        Index('idx_feature_active', 'feature_id', 'is_active'),
    )

    def __repr__(self):
        return f"<LicenseCheckout(username='{self.username}', feature_id={self.feature_id})>"
```

- [ ] **Step 4: Add new models to models/__init__.py**

Modify `backend/app/models/__init__.py` to import the usage models:

```python
# backend/app/models/__init__.py
from app.database import Base
from app.models.server import LicenseServer
from app.models.feature import LicenseFeature
from app.models.usage import LicenseUsageHistory, LicenseCheckout

__all__ = ["Base", "LicenseServer", "LicenseFeature", "LicenseUsageHistory", "LicenseCheckout"]
```

Note: This completes the forward references defined in feature.py

- [ ] **Step 5: Run tests**

```bash
cd backend
pytest tests/test_models_usage.py -v
```

Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add app/models/usage.py app/models/feature.py app/models/__init__.py tests/test_models_usage.py
git commit -m "feat: add LicenseUsageHistory and LicenseCheckout models

Add:
- LicenseUsageHistory for time-series usage data
- LicenseCheckout for current user occupancy
- Cascade delete relationships
- Composite indexes for query performance
- Tests for both models and cascade behavior

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.6: Create Database Models - Alerts & Users

**Files:**
- Create: `backend/app/models/alert.py`
- Create: `backend/app/models/user.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_models_alert.py`
- Create: `backend/tests/test_models_user.py`

- [ ] **Step 1: Write tests for alert models**

```python
# backend/tests/test_models_alert.py
import pytest
from datetime import datetime
from decimal import Decimal
from app.models.alert import AlertRule, AlertLog


def test_create_alert_rule(db_session):
    """Test creating an alert rule"""
    rule = AlertRule(
        name="VCS High Usage Alert",
        rule_type="usage_threshold",
        target_type="feature",
        target_id=1,
        threshold_value=Decimal("90.00"),
        notification_channels={"email": ["admin@example.com"], "dingtalk": ["webhook_url"]},
        enabled=True,
        cooldown_minutes=5
    )

    db_session.add(rule)
    db_session.commit()

    assert rule.id is not None
    assert rule.name == "VCS High Usage Alert"
    assert rule.threshold_value == Decimal("90.00")
    assert "email" in rule.notification_channels


def test_create_alert_log(db_session):
    """Test creating an alert log"""
    # Create rule first
    rule = AlertRule(
        name="Test Rule",
        rule_type="usage_threshold",
        threshold_value=Decimal("90.00")
    )
    db_session.add(rule)
    db_session.commit()

    # Create log
    log = AlertLog(
        rule_id=rule.id,
        triggered_at=datetime.now(),
        severity="critical",
        message="VCS usage at 100%",
        context_data={"feature_id": 1, "usage": 100},
        notified=True
    )

    db_session.add(log)
    db_session.commit()

    assert log.id is not None
    assert log.severity == "critical"
    assert log.rule.name == "Test Rule"


def test_alert_log_cascade_delete(db_session):
    """Test logs are deleted when rule is deleted"""
    rule = AlertRule(name="Test", rule_type="usage_threshold", threshold_value=Decimal("90"))
    db_session.add(rule)
    db_session.commit()

    log = AlertLog(rule_id=rule.id, triggered_at=datetime.now(), severity="warning", message="Test")
    db_session.add(log)
    db_session.commit()

    log_id = log.id

    # Delete rule
    db_session.delete(rule)
    db_session.commit()

    # Log should be deleted
    deleted_log = db_session.query(AlertLog).filter_by(id=log_id).first()
    assert deleted_log is None
```

- [ ] **Step 2: Write tests for user model**

```python
# backend/tests/test_models_user.py
import pytest
from datetime import datetime
from app.models.user import AdminUser, AuditLog


def test_create_admin_user(db_session):
    """Test creating an admin user"""
    user = AdminUser(
        username="admin",
        password_hash="$2b$12$hashed_password_here",
        email="admin@example.com",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "admin"
    assert user.is_active is True


def test_username_unique_constraint(db_session):
    """Test that username must be unique"""
    user1 = AdminUser(username="admin", password_hash="hash1")
    db_session.add(user1)
    db_session.commit()

    # Try to create another user with same username
    user2 = AdminUser(username="admin", password_hash="hash2")
    db_session.add(user2)

    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()


def test_create_audit_log(db_session):
    """Test creating an audit log"""
    user = AdminUser(username="admin", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    audit = AuditLog(
        user_id=user.id,
        action="restart_server",
        resource_type="server",
        resource_id=1,
        details={"server_name": "Synopsys Main"},
        ip_address="192.168.1.100",
        timestamp=datetime.now()
    )

    db_session.add(audit)
    db_session.commit()

    assert audit.id is not None
    assert audit.action == "restart_server"
    assert audit.user.username == "admin"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_models_alert.py tests/test_models_user.py -v
```

Expected: FAIL - ImportError

- [ ] **Step 4: Implement alert models**

```python
# backend/app/models/alert.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, DECIMAL, ForeignKey, func, Index, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AlertRule(Base):
    """Alert rule configuration"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    rule_type = Column(String(50), nullable=False, index=True)  # usage_threshold, server_down
    target_type = Column(String(50))  # server, feature
    target_id = Column(Integer)
    threshold_value = Column(DECIMAL(5, 2))
    notification_channels = Column(JSON)  # {"email": [...], "dingtalk": [...]}
    enabled = Column(Boolean, default=True, index=True)
    cooldown_minutes = Column(Integer, default=5)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    logs = relationship("AlertLog", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', type='{self.rule_type}')>"


class AlertLog(Base):
    """Alert log entries"""
    __tablename__ = "alert_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    triggered_at = Column(DateTime, nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # warning, critical
    message = Column(String, nullable=False)
    context_data = Column(JSON)
    resolved_at = Column(DateTime, index=True)
    notified = Column(Boolean, default=False)
    notification_status = Column(JSON)

    # Relationship
    rule = relationship("AlertRule", back_populates="logs")

    # Index for querying logs by rule and time
    __table_args__ = (
        Index('idx_rule_triggered', 'rule_id', 'triggered_at'),
    )

    def __repr__(self):
        return f"<AlertLog(id={self.id}, severity='{self.severity}', triggered={self.triggered_at})>"
```

- [ ] **Step 5: Implement user models**

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, ForeignKey, func, Index, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AdminUser(Base):
    """Admin user accounts"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}')>"


class AuditLog(Base):
    """Audit trail for admin actions"""
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    # Relationship
    user = relationship("AdminUser", back_populates="audit_logs")

    # Index for querying by user and time
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', timestamp={self.timestamp})>"
```

- [ ] **Step 6: Update models __init__.py**

```python
# backend/app/models/__init__.py
from app.database import Base
from app.models.server import LicenseServer
from app.models.feature import LicenseFeature
from app.models.usage import LicenseUsageHistory, LicenseCheckout
from app.models.alert import AlertRule, AlertLog
from app.models.user import AdminUser, AuditLog

__all__ = [
    "Base",
    "LicenseServer",
    "LicenseFeature",
    "LicenseUsageHistory",
    "LicenseCheckout",
    "AlertRule",
    "AlertLog",
    "AdminUser",
    "AuditLog",
]
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/test_models_alert.py tests/test_models_user.py -v
```

Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add app/models/alert.py app/models/user.py app/models/__init__.py tests/test_models_alert.py tests/test_models_user.py
git commit -m "feat: add AlertRule, AlertLog, AdminUser, and AuditLog models

Add:
- AlertRule model for alert configuration
- AlertLog model for alert history
- AdminUser model for authentication
- AuditLog model for admin action tracking
- JSON columns for flexible data storage
- Tests for all models with cascade behaviors

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.7: Set Up Alembic for Database Migrations

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/001_initial_schema.py`
- Create: `backend/scripts/init_db.py`

- [ ] **Step 1: Initialize Alembic**

```bash
cd backend
alembic init alembic
```

Expected: "Creating directory... Creating environment... Please edit configuration/connection/logging settings..."

This creates:
- `alembic/` directory
- `alembic.ini` file
- `alembic/env.py`
- `alembic/script.py.mako`
- `alembic/versions/` directory

- [ ] **Step 2: Configure alembic.ini**

```ini
# backend/alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://eda_admin:password@localhost:5432/eda_license

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 3: Configure alembic/env.py to use our models**

```python
# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Base and all models
from app.database import Base
from app.models import *
from app.config import settings

# Alembic Config object
config = context.config

# Override sqlalchemy.url from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: Create initial migration**

```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
```

Expected: "Generating alembic/versions/xxxxxxxxxxxx_initial_schema.py ..."

This creates a migration file in `alembic/versions/` with a name like `abc123def456_initial_schema.py` (where the prefix is a timestamp-based revision ID).

**Important:** Review the generated migration file to ensure it correctly creates all 8 tables. Alembic's autogenerate is usually accurate but occasionally misses custom constraints.

- [ ] **Step 5: Create scripts/__init__.py**

```bash
touch backend/scripts/__init__.py
```

This allows scripts to be imported as a module (needed for tests).

- [ ] **Step 6: Create init_db.py script for development**

```python
# backend/scripts/init_db.py
"""Initialize database with all tables"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models import *

def init_db():
    """Create all tables"""
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
```

```bash
chmod +x backend/scripts/init_db.py
```

- [ ] **Step 7: Verify database exists and is accessible**

```bash
psql -U eda_admin -d eda_license -c "SELECT 1"
```

Expected: " ?column? \n----------\n        1"

If you get "database does not exist", you need to create it first (see Task 1.2 Step 5).

- [ ] **Step 8: Test creating the database schema**

```bash
cd backend
python scripts/init_db.py
```

Expected: "Creating all tables... ✓ Database initialized successfully!"

- [ ] **Step 9: Verify tables with psql**

```bash
psql -U eda_admin -d eda_license -c "\dt"
```

Expected: List of exactly 8 tables:
1. license_servers
2. license_features
3. license_usage_history
4. license_checkouts
5. alert_rules
6. alert_logs
7. admin_users
8. audit_logs

- [ ] **Step 10: Commit**

```bash
git add alembic/ alembic.ini scripts/
git commit -m "feat: add Alembic migrations and database initialization

Add:
- Alembic configuration for database migrations
- Initial schema migration with all 8 tables
- init_db.py script for development setup
- scripts/__init__.py for module imports
- Configured env.py to use app models and settings

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.8: Create Sample Data Script

**Files:**
- Create: `backend/scripts/seed_data.py`
- Create: `backend/tests/test_seed_data.py`

- [ ] **Step 1: Write test for seed data**

```python
# backend/tests/test_seed_data.py
import pytest
from app.models import LicenseServer, LicenseFeature, AdminUser
from scripts.seed_data import seed_sample_data


def test_seed_sample_data(db_session):
    """Test that seed data creates expected records"""
    # Seed data
    result = seed_sample_data(db_session)

    # Verify servers created
    servers = db_session.query(LicenseServer).all()
    assert len(servers) == 4  # Synopsys, Cadence, Mentor, Ansys

    # Verify features created
    features = db_session.query(LicenseFeature).all()
    assert len(features) > 0

    # Verify admin user created
    admin = db_session.query(AdminUser).filter_by(username="admin").first()
    assert admin is not None
    assert admin.is_active is True

    assert result["servers"] == 4
    assert result["features"] > 0
    assert result["admin_created"] is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_seed_data.py -v
```

Expected: FAIL - ImportError

- [ ] **Step 3: Implement seed_data.py**

```python
# backend/scripts/seed_data.py
"""Seed database with sample data for development"""
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import LicenseServer, LicenseFeature, AdminUser
from passlib.context import CryptContext

# Note: passlib[bcrypt] is required (installed via requirements.txt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_sample_data(db=None):
    """Seed sample license servers and features"""
    if db is None:
        db = SessionLocal()

    try:
        # Create admin user
        admin = db.query(AdminUser).filter_by(username="admin").first()
        if not admin:
            admin = AdminUser(
                username="admin",
                password_hash=pwd_context.hash("admin123"),
                email="admin@example.com",
                is_active=True
            )
            db.add(admin)
            print("✓ Created admin user (username: admin, password: admin123)")

        # Create license servers
        servers_data = [
            {
                "name": "Synopsys Main",
                "vendor": "synopsys",
                "host": "license-syn-01.eda.local",
                "port": 27000,
                "lmutil_path": "/opt/synopsys/scl/2023.12/linux64/bin",
                "ssh_host": "license-syn-01.eda.local",
                "ssh_user": "admin",
                "status": "active"
            },
            {
                "name": "Cadence Primary",
                "vendor": "cadence",
                "host": "license-cds-01.eda.local",
                "port": 5280,
                "lmutil_path": "/opt/cadence/installs/lmgrd/tools/bin",
                "ssh_host": "license-cds-01.eda.local",
                "ssh_user": "admin",
                "status": "active"
            },
            {
                "name": "Mentor Graphics",
                "vendor": "mentor",
                "host": "license-mtr-01.eda.local",
                "port": 1717,
                "lmutil_path": "/opt/mentor/lmgrd/bin",
                "ssh_host": "license-mtr-01.eda.local",
                "ssh_user": "admin",
                "status": "active"
            },
            {
                "name": "Ansys Server",
                "vendor": "ansys",
                "host": "license-ansys-01.eda.local",
                "port": 2325,
                "lmutil_path": "/opt/ansys/shared_files/licensing/linx64",
                "ssh_host": "license-ansys-01.eda.local",
                "ssh_user": "admin",
                "status": "active"
            }
        ]

        servers_created = 0
        for server_data in servers_data:
            existing = db.query(LicenseServer).filter_by(
                host=server_data["host"]
            ).first()

            if not existing:
                server = LicenseServer(**server_data)
                db.add(server)
                servers_created += 1

        db.commit()
        print(f"✓ Created {servers_created} license servers")

        # Create sample features for each server
        features_data = {
            "Synopsys Main": [
                {"feature_name": "VCS_Runtime", "total_licenses": 200, "version": "2023.12", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "DC-Ultra", "total_licenses": 12, "version": "2023.12", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "ICC-Compiler", "total_licenses": 20, "version": "2023.12", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "PrimeTime", "total_licenses": 30, "version": "2023.12", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Formality", "total_licenses": 15, "version": "2023.12", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "SpyGlass", "total_licenses": 10, "version": "2023.12", "expiry_date": date(2025, 12, 31)},
            ],
            "Cadence Primary": [
                {"feature_name": "virtuoso", "total_licenses": 50, "version": "23.1", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Genus_Synthesis", "total_licenses": 15, "version": "21.1", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Innovus", "total_licenses": 20, "version": "21.1", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Tempus", "total_licenses": 10, "version": "21.1", "expiry_date": date(2025, 12, 31)},
            ],
            "Mentor Graphics": [
                {"feature_name": "Calibre_DRC", "total_licenses": 40, "version": "2023.1", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Calibre_LVS", "total_licenses": 40, "version": "2023.1", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Questa_Sim", "total_licenses": 25, "version": "2023.1", "expiry_date": date(2025, 12, 31)},
            ],
            "Ansys Server": [
                {"feature_name": "HFSS", "total_licenses": 20, "version": "2023R2", "expiry_date": date(2025, 12, 31)},
                {"feature_name": "Maxwell", "total_licenses": 10, "version": "2023R2", "expiry_date": date(2025, 12, 31)},
            ]
        }

        features_created = 0
        for server_name, features in features_data.items():
            server = db.query(LicenseServer).filter_by(name=server_name).first()
            if server:
                for feature_data in features:
                    existing = db.query(LicenseFeature).filter_by(
                        server_id=server.id,
                        feature_name=feature_data["feature_name"]
                    ).first()

                    if not existing:
                        feature = LicenseFeature(
                            server_id=server.id,
                            vendor=server.vendor,
                            **feature_data
                        )
                        db.add(feature)
                        features_created += 1

        db.commit()
        print(f"✓ Created {features_created} license features")

        return {
            "servers": servers_created,
            "features": features_created,
            "admin_created": True
        }

    finally:
        if db:
            db.close()


if __name__ == "__main__":
    print("Seeding sample data...")
    result = seed_sample_data()
    print(f"\n✓ Seed complete!")
    print(f"  - Servers: {result['servers']}")
    print(f"  - Features: {result['features']}")
    print(f"  - Admin user: admin/admin123")
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_seed_data.py -v
```

Expected: PASS

- [ ] **Step 5: Run seed script on development database**

```bash
cd backend
python scripts/seed_data.py
```

Expected: Sample data created

- [ ] **Step 6: Verify data**

```bash
psql -U eda_admin -d eda_license -c "SELECT name, vendor FROM license_servers;"
psql -U eda_admin -d eda_license -c "SELECT feature_name, total_licenses FROM license_features LIMIT 10;"
```

Expected: Sample servers and features listed

- [ ] **Step 7: Commit**

```bash
git add scripts/seed_data.py tests/test_seed_data.py
git commit -m "feat: add sample data seeding script

Add:
- seed_data.py script to populate development database
- Creates 4 license servers (Synopsys, Cadence, Mentor, Ansys)
- Creates 20+ license features across servers
- Creates default admin user (admin/admin123)
- Tests for seed data generation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 1.9: End-to-End Integration Test

**Files:**
- Create: `backend/tests/test_integration.py`

**Goal:** Verify all models work together in realistic usage scenarios.

- [ ] **Step 1: Write integration test**

```python
# backend/tests/test_integration.py
import pytest
from datetime import datetime, date
from decimal import Decimal
from app.models import (
    LicenseServer, LicenseFeature, LicenseUsageHistory,
    LicenseCheckout, AlertRule, AlertLog, AdminUser, AuditLog
)


def test_complete_license_workflow(db_session):
    """Test complete workflow: server -> features -> usage -> checkouts"""
    # 1. Create server
    server = LicenseServer(
        name="Test Synopsys",
        vendor="synopsys",
        host="test.eda.local",
        port=27000,
        status="active"
    )
    db_session.add(server)
    db_session.commit()

    # 2. Create features for server
    vcs_feature = LicenseFeature(
        server_id=server.id,
        feature_name="VCS_Runtime",
        total_licenses=200,
        vendor="synopsys",
        expiry_date=date(2025, 12, 31)
    )
    db_session.add(vcs_feature)
    db_session.commit()

    # 3. Record usage history
    usage = LicenseUsageHistory(
        feature_id=vcs_feature.id,
        timestamp=datetime.now(),
        used_count=156,
        available_count=44,
        usage_percentage=Decimal("78.00")
    )
    db_session.add(usage)
    db_session.commit()

    # 4. Create checkout
    checkout = LicenseCheckout(
        feature_id=vcs_feature.id,
        username="test.user",
        hostname="ws-01.local",
        checkout_time=datetime.now(),
        is_active=True
    )
    db_session.add(checkout)
    db_session.commit()

    # Verify relationships work
    assert len(server.features) == 1
    assert server.features[0].feature_name == "VCS_Runtime"
    assert len(vcs_feature.usage_history) == 1
    assert len(vcs_feature.checkouts) == 1


def test_alert_workflow(db_session):
    """Test alert rule creation and logging"""
    # 1. Create admin user
    admin = AdminUser(
        username="test_admin",
        password_hash="hashed_pw",
        email="admin@test.com",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    # 2. Create alert rule
    rule = AlertRule(
        name="High Usage Alert",
        rule_type="usage_threshold",
        target_type="feature",
        target_id=1,
        threshold_value=Decimal("90.00"),
        enabled=True,
        notification_channels={"email": ["admin@test.com"]}
    )
    db_session.add(rule)
    db_session.commit()

    # 3. Trigger alert
    alert = AlertLog(
        rule_id=rule.id,
        triggered_at=datetime.now(),
        severity="critical",
        message="Test alert",
        notified=True
    )
    db_session.add(alert)
    db_session.commit()

    # 4. Record audit log
    audit = AuditLog(
        user_id=admin.id,
        action="create_alert_rule",
        resource_type="alert_rule",
        resource_id=rule.id,
        ip_address="127.0.0.1",
        details={"rule_name": rule.name}
    )
    db_session.add(audit)
    db_session.commit()

    # Verify relationships
    assert len(rule.logs) == 1
    assert len(admin.audit_logs) == 1
    assert alert.rule.name == "High Usage Alert"


def test_cascade_delete(db_session):
    """Test cascade delete behavior across all models"""
    # Create server with full hierarchy
    server = LicenseServer(
        name="Delete Test",
        vendor="test",
        host="delete.local",
        port=27000
    )
    db_session.add(server)
    db_session.commit()

    feature = LicenseFeature(
        server_id=server.id,
        feature_name="TestFeature",
        total_licenses=10
    )
    db_session.add(feature)
    db_session.commit()

    usage = LicenseUsageHistory(
        feature_id=feature.id,
        timestamp=datetime.now(),
        used_count=5,
        available_count=5,
        usage_percentage=Decimal("50.00")
    )
    checkout = LicenseCheckout(
        feature_id=feature.id,
        username="user1",
        hostname="host1",
        checkout_time=datetime.now()
    )
    db_session.add_all([usage, checkout])
    db_session.commit()

    feature_id = feature.id
    usage_id = usage.id
    checkout_id = checkout.id

    # Delete server - should cascade to feature, usage, checkout
    db_session.delete(server)
    db_session.commit()

    # Verify cascade
    assert db_session.query(LicenseFeature).filter_by(id=feature_id).first() is None
    assert db_session.query(LicenseUsageHistory).filter_by(id=usage_id).first() is None
    assert db_session.query(LicenseCheckout).filter_by(id=checkout_id).first() is None
```

- [ ] **Step 2: Run integration tests**

```bash
cd backend
pytest tests/test_integration.py -v
```

Expected: 3/3 tests PASS

- [ ] **Step 3: Run ALL tests to ensure nothing broke**

```bash
pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration tests

Add:
- Complete license workflow test (server -> feature -> usage -> checkout)
- Alert workflow test (user -> rule -> log -> audit)
- Cascade delete behavior test
- Verifies all models work together correctly

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Chunk 1 Complete

**Checkpoint:** You now have:
✅ Backend project structure with configuration
✅ Database connection with SQLAlchemy
✅ All 8 database models (Server, Feature, Usage, Checkouts, Alerts, Users, Audits)
✅ Alembic migrations setup
✅ Sample data seeding script
✅ Comprehensive tests for all models

**Test the foundation:**

```bash
cd backend

# Run all tests
pytest -v

# Verify database
psql -U eda_admin -d eda_license -c "\dt"

# Check sample data
python scripts/seed_data.py
```

**Next:** Chunk 2 will build the License Collector (lmstat parser + Celery tasks).

