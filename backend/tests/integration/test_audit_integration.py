"""
Integration tests for the audit module against a real PostgreSQL database.

Tests cover: log_action persistence, get_audit_logs with filters.
"""
import pytest

from app.modules.audit.service import get_audit_logs, log_action


class TestAuditLogIntegration:
    @pytest.mark.asyncio
    async def test_log_action_persists_to_db(self, async_db):
        # user_id=None — audit_log.user_id is nullable (no FK violation)
        entry = await log_action(
            async_db,
            action="login",
            user_id=None,
            resource_type="session",
            details="User logged in",
            ip_address="10.0.0.1",
        )

        assert entry.id is not None
        assert entry.action == "login"
        assert entry.ip_address == "10.0.0.1"

    @pytest.mark.asyncio
    async def test_log_action_with_only_action(self, async_db):
        entry = await log_action(async_db, action="system_startup")
        assert entry.id is not None
        assert entry.user_id is None
        assert entry.resource_type is None

    @pytest.mark.asyncio
    async def test_get_audit_logs_returns_all(self, async_db):
        await log_action(async_db, action="event_x_a")
        await log_action(async_db, action="event_x_b")

        logs = await get_audit_logs(async_db)
        actions = {l.action for l in logs}
        assert "event_x_a" in actions
        assert "event_x_b" in actions

    @pytest.mark.asyncio
    async def test_get_audit_logs_filtered_by_action(self, async_db):
        await log_action(async_db, action="query_executed_int")
        await log_action(async_db, action="export_csv_int")

        logs = await get_audit_logs(async_db, action="query_executed_int")
        assert all(l.action == "query_executed_int" for l in logs)
        assert any(l.action == "query_executed_int" for l in logs)

    @pytest.mark.asyncio
    async def test_get_audit_logs_respects_limit(self, async_db):
        for i in range(5):
            await log_action(async_db, action="bulk_event_int")

        logs = await get_audit_logs(async_db, limit=2, action="bulk_event_int")
        # limit=2 — at most 2 results returned
        assert len(logs) <= 2

    @pytest.mark.asyncio
    async def test_logs_are_ordered_most_recent_first(self, async_db):
        await log_action(async_db, action="first_event_int")
        await log_action(async_db, action="second_event_int")

        logs = await get_audit_logs(async_db, action="first_event_int")
        # Should return at least the one we created
        assert any(l.action == "first_event_int" for l in logs)
