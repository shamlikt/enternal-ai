"""
Integration tests for the auth module against a real PostgreSQL database.

Tests cover the full cycle: create user → authenticate → update → deactivate.
Uses a testcontainers disposable PostgreSQL instance (no shared state).
"""
import pytest

from app.core.security import get_password_hash, verify_password
from app.modules.auth.models import Role, User
from app.modules.auth.schemas import UserCreate, UserUpdate
from app.modules.auth.service import (
    authenticate_user,
    create_user,
    deactivate_user,
    get_user_by_id,
    get_user_by_username,
    get_users,
    update_user,
)


class TestUserCRUDIntegration:
    @pytest.mark.asyncio
    async def test_create_and_retrieve_user(self, async_db):
        user_data = UserCreate(
            username="alice_int",
            email="alice_int@example.com",
            password="securepass1",
            role=Role.ANALYST,
        )
        user = await create_user(async_db, user_data)

        assert user.id is not None
        assert user.username == "alice_int"
        assert user.role == Role.ANALYST
        assert user.is_active is True
        # Password should be hashed
        assert user.password_hash != "securepass1"
        assert verify_password("securepass1", user.password_hash)

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, async_db):
        user_data = UserCreate(
            username="bob_int",
            email="bob_int@example.com",
            password="securepass1",
        )
        created = await create_user(async_db, user_data)

        found = await get_user_by_username(async_db, "bob_int")
        assert found is not None
        assert found.id == created.id

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, async_db):
        result = await get_user_by_username(async_db, "nonexistent_user")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_db):
        user_data = UserCreate(
            username="carol_int",
            email="carol_int@example.com",
            password="securepass1",
        )
        created = await create_user(async_db, user_data)

        found = await get_user_by_id(async_db, created.id)
        assert found is not None
        assert found.username == "carol_int"

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, async_db):
        result = await get_user_by_id(async_db, 999999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_users_returns_created_users(self, async_db):
        # Create two users
        await create_user(async_db, UserCreate(
            username="dave_int", email="dave_int@example.com", password="securepass1"
        ))
        await create_user(async_db, UserCreate(
            username="eve_int", email="eve_int@example.com", password="securepass1"
        ))

        users = await get_users(async_db)
        usernames = {u.username for u in users}
        assert "dave_int" in usernames
        assert "eve_int" in usernames

    @pytest.mark.asyncio
    async def test_update_user_role(self, async_db):
        created = await create_user(async_db, UserCreate(
            username="frank_int", email="frank_int@example.com", password="securepass1"
        ))
        assert created.role == Role.VIEWER

        updated = await update_user(async_db, created, UserUpdate(role=Role.ANALYST))
        assert updated.role == Role.ANALYST

    @pytest.mark.asyncio
    async def test_deactivate_user(self, async_db):
        created = await create_user(async_db, UserCreate(
            username="grace_int", email="grace_int@example.com", password="securepass1"
        ))
        assert created.is_active is True

        deactivated = await deactivate_user(async_db, created)
        assert deactivated.is_active is False


class TestAuthenticateUserIntegration:
    @pytest.mark.asyncio
    async def test_authenticate_returns_user_with_correct_password(self, async_db):
        await create_user(async_db, UserCreate(
            username="harry_int", email="harry_int@example.com", password="correctpassword"
        ))

        result = await authenticate_user(async_db, "harry_int", "correctpassword")
        assert result is not None
        assert result.username == "harry_int"

    @pytest.mark.asyncio
    async def test_authenticate_returns_none_for_wrong_password(self, async_db):
        await create_user(async_db, UserCreate(
            username="ivan_int", email="ivan_int@example.com", password="correctpassword"
        ))

        result = await authenticate_user(async_db, "ivan_int", "wrongpassword")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_returns_none_for_nonexistent_user(self, async_db):
        result = await authenticate_user(async_db, "ghost_int", "anypassword")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_returns_none_for_inactive_user(self, async_db):
        created = await create_user(async_db, UserCreate(
            username="judy_int", email="judy_int@example.com", password="correctpassword"
        ))
        await deactivate_user(async_db, created)

        # Inactive user should not be returned by authenticate_user
        result = await authenticate_user(async_db, "judy_int", "correctpassword")
        assert result is None
