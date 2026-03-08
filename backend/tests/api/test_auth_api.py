"""
API contract tests for /api/v1/auth/* and /api/v1/users/* endpoints.

Tests HTTP status codes, response shapes, and authorization enforcement.
No real DB or network — service calls are mocked via dependency_overrides.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.auth.models import Role, User
from app.modules.auth.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.security import get_password_hash

from tests.api.conftest import _make_user, make_mock_db


def _make_hashed_user(username: str = "alice", password: str = "correctpassword") -> User:
    user = _make_user(username=username, role=Role.ADMIN)
    user.password_hash = get_password_hash(password)
    return user


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------


class TestLoginEndpoint:
    @pytest.mark.asyncio
    async def test_valid_credentials_returns_token(self):
        user = _make_hashed_user(username="alice", password="correctpassword")
        mock_db = make_mock_db(scalar_result=user)
        app.dependency_overrides[get_db] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/auth/login",
                data={"username": "alice", "password": "correctpassword"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_wrong_password_returns_401(self):
        user = _make_hashed_user(username="alice", password="correctpassword")
        mock_db = make_mock_db(scalar_result=user)
        app.dependency_overrides[get_db] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/auth/login",
                data={"username": "alice", "password": "wrongpassword"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_nonexistent_user_returns_401(self):
        mock_db = make_mock_db(scalar_result=None)
        app.dependency_overrides[get_db] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/auth/login",
                data={"username": "ghost", "password": "anypassword"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_credentials_returns_422(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/auth/login", data={})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/auth/me
# ---------------------------------------------------------------------------


class TestMeEndpoint:
    @pytest.mark.asyncio
    async def test_returns_current_user(self):
        user = _make_user(username="alice", role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: user

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/auth/me")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "alice"
        assert body["role"] == "analyst"

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/logout
# ---------------------------------------------------------------------------


class TestLogoutEndpoint:
    @pytest.mark.asyncio
    async def test_logout_returns_200(self):
        user = _make_user(role=Role.ADMIN)
        app.dependency_overrides[get_current_user] = lambda: user

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/auth/logout")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        assert "message" in resp.json()


# ---------------------------------------------------------------------------
# GET /api/v1/users/ (admin only)
# ---------------------------------------------------------------------------


class TestUsersEndpoint:
    @pytest.mark.asyncio
    async def test_admin_can_list_users(self):
        admin = _make_user(role=Role.ADMIN)
        u1 = _make_user(user_id=1, username="alice")
        u2 = _make_user(user_id=2, username="bob")

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [u1, u2]
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        # Override get_current_user — require_role internally calls it via Depends,
        # so overriding get_current_user propagates through all role-checking deps.
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/users/")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        usernames = {u["username"] for u in body}
        assert "alice" in usernames
        assert "bob" in usernames

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/users/")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_returns_201(self):
        admin = _make_user(role=Role.ADMIN)

        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()

        def _refresh_user(u):
            u.id = 99
            u.is_active = True
            u.created_at = datetime.now(timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=_refresh_user)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/users/",
                json={
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "securepass1",
                    "role": "viewer",
                },
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_update_nonexistent_user_returns_404(self):
        admin = _make_user(role=Role.ADMIN)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.patch("/api/v1/users/9999", json={"role": "analyst"})

        app.dependency_overrides.clear()
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user_returns_404(self):
        admin = _make_user(role=Role.ADMIN)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/api/v1/users/9999")

        app.dependency_overrides.clear()
        assert resp.status_code == 404
