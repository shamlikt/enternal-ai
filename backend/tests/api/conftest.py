"""
Shared fixtures for API contract tests.

Uses FastAPI dependency_overrides to inject:
- A mock AsyncSession (no real DB needed)
- A fake authenticated user (no real JWT verification)
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.modules.auth.models import Role, User
from app.modules.auth.dependencies import get_current_user, require_role
from app.core.database import get_db


def _make_user(
    user_id: int = 1,
    username: str = "testuser",
    role: Role = Role.ADMIN,
    is_active: bool = True,
) -> User:
    user = User()
    user.id = user_id
    user.username = username
    user.email = f"{username}@example.com"
    user.role = role
    user.is_active = is_active
    user.created_at = datetime.now(timezone.utc)
    user.password_hash = "hashed"
    return user


def make_mock_db(
    scalar_result=None,
    scalars_result=None,
    execute_side_effect=None,
) -> AsyncMock:
    """Build a mock AsyncSession."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_result
    result.scalars.return_value.all.return_value = scalars_result or []
    result.fetchall.return_value = []
    if execute_side_effect:
        db.execute.side_effect = execute_side_effect
    else:
        db.execute.return_value = result
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Ensure dependency_overrides is always clean before and after each test."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user() -> User:
    return _make_user(role=Role.ADMIN)


@pytest.fixture
def analyst_user() -> User:
    return _make_user(role=Role.ANALYST, username="analyst")


@pytest.fixture
def viewer_user() -> User:
    return _make_user(role=Role.VIEWER, username="viewer")


@pytest.fixture
def mock_db() -> AsyncMock:
    return make_mock_db()


@pytest.fixture
async def admin_client(admin_user: User, mock_db: AsyncMock) -> AsyncClient:
    """Async HTTP client authenticated as admin."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: admin_user
    # Override all role variants
    for roles in [
        (Role.ADMIN,),
        (Role.ADMIN, Role.ANALYST),
        (Role.ANALYST,),
    ]:
        app.dependency_overrides[require_role(*roles)] = lambda u=admin_user: u

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def analyst_client(analyst_user: User, mock_db: AsyncMock) -> AsyncClient:
    """Async HTTP client authenticated as analyst."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: analyst_user
    for roles in [
        (Role.ADMIN, Role.ANALYST),
        (Role.ANALYST,),
    ]:
        app.dependency_overrides[require_role(*roles)] = lambda u=analyst_user: u
    # Block admin-only endpoints
    app.dependency_overrides[require_role(Role.ADMIN)] = lambda: (_ for _ in ()).throw(
        __import__("fastapi").HTTPException(status_code=403, detail="Insufficient permissions")
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def unauthenticated_client() -> AsyncClient:
    """Async HTTP client with NO auth overrides — tests 401 responses."""
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
