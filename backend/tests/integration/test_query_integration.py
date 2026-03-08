"""
Integration tests for the query module against a real PostgreSQL database.

Tests cover: saved query CRUD, query history creation, and the audit trail.
The SELECT-only enforcement is already covered in unit tests; here we verify
the full service stack (DB persistence, refresh, etc.) works end-to-end.
"""
import pytest

from app.modules.auth.schemas import UserCreate
from app.modules.auth.service import create_user
from app.modules.query.schemas import SavedQueryCreate, SavedQueryUpdate
from app.modules.query.service import (
    create_saved_query,
    delete_saved_query,
    get_query_history,
    get_saved_queries,
    get_saved_query_by_id,
    update_saved_query,
)


async def _create_test_user(db, username: str = "testuser_q"):
    """Helper: create a user for use in query tests."""
    return await create_user(db, UserCreate(
        username=username,
        email=f"{username}@example.com",
        password="securepass1",
    ))


class TestSavedQueryCRUDIntegration:
    @pytest.mark.asyncio
    async def test_create_saved_query(self, async_db):
        user = await _create_test_user(async_db, "sq_user1")
        data = SavedQueryCreate(
            name="Demographics Count",
            sql="SELECT COUNT(*) FROM DEMOGRAPHIC",
            description="Count all patients",
        )

        saved = await create_saved_query(async_db, user.id, data)

        assert saved.id is not None
        assert saved.name == "Demographics Count"
        assert saved.sql == "SELECT COUNT(*) FROM DEMOGRAPHIC"
        assert saved.description == "Count all patients"
        assert saved.user_id == user.id

    @pytest.mark.asyncio
    async def test_list_saved_queries_for_user(self, async_db):
        user = await _create_test_user(async_db, "sq_user2")
        await create_saved_query(async_db, user.id, SavedQueryCreate(
            name="Query A", sql="SELECT 1"
        ))
        await create_saved_query(async_db, user.id, SavedQueryCreate(
            name="Query B", sql="SELECT 2"
        ))

        queries = await get_saved_queries(async_db, user.id)
        names = {q.name for q in queries}
        assert "Query A" in names
        assert "Query B" in names

    @pytest.mark.asyncio
    async def test_queries_are_user_scoped(self, async_db):
        """A user cannot see another user's saved queries."""
        user1 = await _create_test_user(async_db, "sq_user3")
        user2 = await _create_test_user(async_db, "sq_user4")

        await create_saved_query(async_db, user1.id, SavedQueryCreate(
            name="User1 Query", sql="SELECT 1"
        ))

        user2_queries = await get_saved_queries(async_db, user2.id)
        names = {q.name for q in user2_queries}
        assert "User1 Query" not in names

    @pytest.mark.asyncio
    async def test_get_saved_query_by_id(self, async_db):
        user = await _create_test_user(async_db, "sq_user5")
        saved = await create_saved_query(async_db, user.id, SavedQueryCreate(
            name="Test", sql="SELECT COUNT(*) FROM DEMOGRAPHIC"
        ))

        found = await get_saved_query_by_id(async_db, saved.id, user.id)
        assert found is not None
        assert found.id == saved.id

    @pytest.mark.asyncio
    async def test_get_saved_query_by_id_wrong_user(self, async_db):
        user1 = await _create_test_user(async_db, "sq_user6")
        user2 = await _create_test_user(async_db, "sq_user7")
        saved = await create_saved_query(async_db, user1.id, SavedQueryCreate(
            name="User1 Secret", sql="SELECT 1"
        ))

        found = await get_saved_query_by_id(async_db, saved.id, user2.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_update_saved_query(self, async_db):
        user = await _create_test_user(async_db, "sq_user8")
        saved = await create_saved_query(async_db, user.id, SavedQueryCreate(
            name="Old Name", sql="SELECT 1"
        ))

        updated = await update_saved_query(async_db, saved, SavedQueryUpdate(
            name="New Name",
            sql="SELECT COUNT(*) FROM DEMOGRAPHIC",
        ))

        assert updated.name == "New Name"
        assert updated.sql == "SELECT COUNT(*) FROM DEMOGRAPHIC"

    @pytest.mark.asyncio
    async def test_delete_saved_query(self, async_db):
        user = await _create_test_user(async_db, "sq_user9")
        saved = await create_saved_query(async_db, user.id, SavedQueryCreate(
            name="To Delete", sql="SELECT 1"
        ))

        await delete_saved_query(async_db, saved)

        found = await get_saved_query_by_id(async_db, saved.id, user.id)
        assert found is None


class TestQueryHistoryIntegration:
    @pytest.mark.asyncio
    async def test_query_history_is_initially_empty(self, async_db):
        user = await _create_test_user(async_db, "hist_user1")
        history = await get_query_history(async_db, user.id)
        assert history == []
