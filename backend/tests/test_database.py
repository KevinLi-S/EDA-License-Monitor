"""Tests for database connection"""
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from app.database import get_engine, get_session


def test_get_engine_returns_async_engine():
    """Test that get_engine returns an AsyncEngine instance"""
    engine = get_engine()
    assert isinstance(engine, AsyncEngine)
    assert engine is not None


@pytest.mark.asyncio
async def test_get_session_returns_session():
    """Test that get_session yields a valid session"""
    async for session in get_session():
        assert session is not None
        # Session should have required methods
        assert hasattr(session, 'execute')
        assert hasattr(session, 'commit')
        assert hasattr(session, 'rollback')
