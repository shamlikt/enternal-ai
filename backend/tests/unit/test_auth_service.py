"""
Unit tests for app.modules.auth.service and app.modules.auth.schemas.

Tests use AsyncMock to simulate DB operations without a real database.
Auth logic (password hashing, token creation) is tested via real implementations.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.core.security import create_access_token, get_password_hash
from app.modules.auth.models import Role, User
from app.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.modules.auth.service import (
    authenticate_user,
    create_user,
    deactivate_user,
    get_user_by_id,
    get_user_by_username,
    get_users,
    update_user,
)


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestLoginRequest:
    def test_valid_login_request(self):
        req = LoginRequest(username="alice", password="secretpassword")
        assert req.username == "alice"

    def test_missing_username_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="secret")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="alice")


class TestUserCreate:
    def test_valid_create(self):
        uc = UserCreate(
            username="alice",
            email="alice@example.com",
            password="securepass1",
        )
        assert uc.role == Role.VIEWER  # default

    def test_admin_role(self):
        uc = UserCreate(
            username="admin",
            email="admin@example.com",
            password="securepass1",
            role=Role.ADMIN,
        )
        assert uc.role == Role.ADMIN

    def test_username_too_short_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(username="ab", email="a@b.com", password="securepass1")

    def test_username_too_long_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(username="a" * 101, email="a@b.com", password="securepass1")

    def test_password_too_short_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", email="alice@example.com", password="short")

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", email="not-an-email", password="securepass1")

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", password="securepass1")


class TestUserUpdate:
    def test_all_optional(self):
        update = UserUpdate()
        assert update.email is None
        assert update.role is None
        assert update.is_active is None

    def test_partial_role_update(self):
        update = UserUpdate(role=Role.ANALYST)
        assert update.role == Role.ANALYST

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserUpdate(email="bad-email")


class TestUserResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = UserResponse(
            id=1,
            username="alice",
            email="alice@example.com",
            role=Role.ANALYST,
            is_active=True,
            created_at=now,
        )
        assert resp.id == 1
        assert resp.role == Role.ANALYST

    def test_missing_id_raises(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            UserResponse(
                username="alice",
                email="alice@example.com",
                role=Role.VIEWER,
                is_active=True,
                created_at=now,
            )


class TestTokenResponse:
    def test_default_token_type(self):
        resp = TokenResponse(access_token="mytoken.abc.def")
        assert resp.token_type == "bearer"

    def test_custom_access_token(self):
        token = create_access_token({"sub": "alice"})
        resp = TokenResponse(access_token=token)
        assert resp.access_token == token


# ---------------------------------------------------------------------------
# Service unit tests (using mocked AsyncSession)
# ---------------------------------------------------------------------------


def _make_user(
    user_id: int = 1,
    username: str = "alice",
    email: str = "alice@example.com",
    role: Role = Role.VIEWER,
    is_active: bool = True,
    password: str = "securepass1",
) -> User:
    """Factory: create a User ORM object with a hashed password."""
    user = User()
    user.id = user_id
    user.username = username
    user.email = email
    user.role = role
    user.is_active = is_active
    user.password_hash = get_password_hash(password)
    user.created_at = datetime.now(timezone.utc)
    return user


def _make_mock_db(scalar_result=None):
    """Create a mock AsyncSession that returns a configured scalar result."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_result
    result.scalars.return_value.all.return_value = [scalar_result] if scalar_result else []
    db.execute.return_value = result
    return db


class TestAuthenticateUser:
    @pytest.mark.asyncio
    async def test_valid_credentials_returns_user(self):
        user = _make_user(password="correctpassword")
        db = _make_mock_db(scalar_result=user)
        result = await authenticate_user(db, "alice", "correctpassword")
        assert result is user

    @pytest.mark.asyncio
    async def test_wrong_password_returns_none(self):
        user = _make_user(password="correctpassword")
        db = _make_mock_db(scalar_result=user)
        result = await authenticate_user(db, "alice", "wrongpassword")
        assert result is None

    @pytest.mark.asyncio
    async def test_nonexistent_user_returns_none(self):
        db = _make_mock_db(scalar_result=None)
        result = await authenticate_user(db, "nonexistent", "anypassword")
        assert result is None

    @pytest.mark.asyncio
    async def test_inactive_user_not_returned(self):
        """authenticate_user queries with is_active=True so inactive users won't match."""
        # The mock returns None to simulate no active user found
        db = _make_mock_db(scalar_result=None)
        result = await authenticate_user(db, "alice", "correctpassword")
        assert result is None


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user_hashes_password(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        user_data = UserCreate(
            username="bob",
            email="bob@example.com",
            password="securepass1",
            role=Role.ANALYST,
        )

        result = await create_user(db, user_data)

        db.add.assert_called_once()
        await db.commit()

        # Verify the object passed to add() has a hashed (not plain) password.
        added_user = db.add.call_args[0][0]
        assert added_user.username == "bob"
        assert added_user.password_hash != "securepass1"
        assert added_user.role == Role.ANALYST

    @pytest.mark.asyncio
    async def test_create_user_default_role_viewer(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        user_data = UserCreate(
            username="carol",
            email="carol@example.com",
            password="securepass1",
        )

        await create_user(db, user_data)
        added_user = db.add.call_args[0][0]
        assert added_user.role == Role.VIEWER


class TestGetUsers:
    @pytest.mark.asyncio
    async def test_returns_list_of_users(self):
        user1 = _make_user(user_id=1, username="alice")
        user2 = _make_user(user_id=2, username="bob")
        db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [user1, user2]
        db.execute.return_value = result

        users = await get_users(db)
        assert len(users) == 2
        assert users[0].username == "alice"
        assert users[1].username == "bob"

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_users(self):
        db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        db.execute.return_value = result

        users = await get_users(db)
        assert users == []


class TestGetUserByUsername:
    @pytest.mark.asyncio
    async def test_found_user(self):
        user = _make_user(username="alice")
        db = _make_mock_db(scalar_result=user)
        found = await get_user_by_username(db, "alice")
        assert found is user

    @pytest.mark.asyncio
    async def test_not_found_returns_none(self):
        db = _make_mock_db(scalar_result=None)
        found = await get_user_by_username(db, "ghost")
        assert found is None


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_role(self):
        user = _make_user(role=Role.VIEWER)
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        update_data = UserUpdate(role=Role.ADMIN)
        result = await update_user(db, user, update_data)

        assert user.role == Role.ADMIN
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_email(self):
        user = _make_user(email="old@example.com")
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        update_data = UserUpdate(email="new@example.com")
        await update_user(db, user, update_data)
        assert user.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_partial_update_leaves_other_fields_unchanged(self):
        user = _make_user(role=Role.ANALYST, email="alice@example.com")
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        update_data = UserUpdate(is_active=False)
        await update_user(db, user, update_data)

        assert user.role == Role.ANALYST  # unchanged
        assert user.email == "alice@example.com"  # unchanged
        assert user.is_active is False


class TestDeactivateUser:
    @pytest.mark.asyncio
    async def test_deactivate_sets_is_active_false(self):
        user = _make_user(is_active=True)
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        await deactivate_user(db, user)

        assert user.is_active is False
        db.commit.assert_called_once()
