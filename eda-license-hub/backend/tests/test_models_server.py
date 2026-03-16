import pytest
from datetime import datetime
from app.models.server import LicenseServer


@pytest.mark.asyncio
async def test_create_license_server(test_session):
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

    test_session.add(server)
    await test_session.commit()

    assert server.id is not None
    assert server.name == "Synopsys Main"
    assert server.vendor == "synopsys"
    assert server.created_at is not None


@pytest.mark.asyncio
async def test_license_server_relationships(test_session):
    """Test that server can have features"""
    server = LicenseServer(
        name="Test Server",
        vendor="synopsys",
        host="test.local",
        port=27000
    )

    test_session.add(server)
    await test_session.commit()

    # Refresh to load relationships explicitly for async session
    await test_session.refresh(server, attribute_names=["features"])

    # Should have empty features list initially
    assert list(server.features) == []
