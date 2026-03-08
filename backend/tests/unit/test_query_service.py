"""
Unit tests for app.modules.query.service and app.modules.query.schemas.

Critical: The SELECT-only guardrail (_validate_select_only) must reject all DDL
and DML statements to prevent unauthorized data modification via the SQL editor
or AI agent.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.modules.query.schemas import (
    ColumnInfo,
    QueryExecuteRequest,
    QueryExecuteResponse,
    QueryHistoryResponse,
    SavedQueryCreate,
    SavedQueryResponse,
    SavedQueryUpdate,
)
from app.modules.query.service import _validate_select_only


# ---------------------------------------------------------------------------
# SELECT-only guardrail tests (the most critical security control)
# ---------------------------------------------------------------------------


class TestSelectOnlyValidation:
    """_validate_select_only raises HTTPException(400) for any non-SELECT SQL."""

    def test_select_statement_is_allowed(self):
        """Valid SELECT should not raise."""
        _validate_select_only("SELECT * FROM DEMOGRAPHIC")

    def test_select_with_where_is_allowed(self):
        _validate_select_only("SELECT PATID, SEX FROM DEMOGRAPHIC WHERE RACE = '05'")

    def test_select_with_join_is_allowed(self):
        _validate_select_only(
            "SELECT d.PATID, e.ENC_TYPE FROM DEMOGRAPHIC d JOIN ENCOUNTER e ON d.PATID = e.PATID"
        )

    def test_select_with_subquery_is_allowed(self):
        _validate_select_only("SELECT * FROM (SELECT PATID FROM DEMOGRAPHIC) AS sub")

    def test_select_with_cte_is_allowed(self):
        _validate_select_only(
            "WITH cte AS (SELECT PATID FROM DEMOGRAPHIC) SELECT * FROM cte"
        )

    def test_select_with_limit_is_allowed(self):
        _validate_select_only("SELECT PATID FROM DEMOGRAPHIC LIMIT 10")

    def test_insert_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("INSERT INTO DEMOGRAPHIC (PATID) VALUES ('PAT001')")
        assert exc_info.value.status_code == 400

    def test_update_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("UPDATE DEMOGRAPHIC SET SEX = 'F' WHERE PATID = 'PAT001'")
        assert exc_info.value.status_code == 400

    def test_delete_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("DELETE FROM DEMOGRAPHIC WHERE PATID = 'PAT001'")
        assert exc_info.value.status_code == 400

    def test_drop_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("DROP TABLE DEMOGRAPHIC")
        assert exc_info.value.status_code == 400

    def test_alter_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("ALTER TABLE DEMOGRAPHIC ADD COLUMN new_col VARCHAR(10)")
        assert exc_info.value.status_code == 400

    def test_create_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("CREATE TABLE evil_table (id INT)")
        assert exc_info.value.status_code == 400

    def test_truncate_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("TRUNCATE TABLE DEMOGRAPHIC")
        assert exc_info.value.status_code == 400

    def test_merge_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("MERGE INTO DEMOGRAPHIC USING source ON (1=1) WHEN MATCHED THEN UPDATE")
        assert exc_info.value.status_code == 400

    def test_exec_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("EXEC sp_helpdb")
        assert exc_info.value.status_code == 400

    def test_grant_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("GRANT ALL ON DEMOGRAPHIC TO public")
        assert exc_info.value.status_code == 400

    def test_revoke_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("REVOKE SELECT ON DEMOGRAPHIC FROM analyst")
        assert exc_info.value.status_code == 400

    def test_case_insensitive_insert_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("insert into DEMOGRAPHIC (PATID) values ('test')")
        assert exc_info.value.status_code == 400

    def test_case_insensitive_update_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("UPDATE demographic set sex = 'M'")
        assert exc_info.value.status_code == 400

    def test_leading_whitespace_insert_is_rejected(self):
        """Leading whitespace should not bypass the check."""
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("   INSERT INTO DEMOGRAPHIC VALUES ('x')")
        assert exc_info.value.status_code == 400

    def test_leading_newline_delete_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("\n\nDELETE FROM DEMOGRAPHIC")
        assert exc_info.value.status_code == 400

    def test_replace_is_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("REPLACE INTO DEMOGRAPHIC VALUES ('PAT001', '1980-01-01')")
        assert exc_info.value.status_code == 400

    def test_error_message_mentions_select_only(self):
        with pytest.raises(HTTPException) as exc_info:
            _validate_select_only("DROP TABLE DEMOGRAPHIC")
        assert "SELECT" in exc_info.value.detail


# ---------------------------------------------------------------------------
# Query schema tests
# ---------------------------------------------------------------------------


class TestQueryExecuteRequest:
    def test_valid_sql(self):
        req = QueryExecuteRequest(sql="SELECT * FROM DEMOGRAPHIC")
        assert req.sql == "SELECT * FROM DEMOGRAPHIC"

    def test_empty_sql_raises(self):
        with pytest.raises(ValidationError):
            QueryExecuteRequest(sql="")

    def test_missing_sql_raises(self):
        with pytest.raises(ValidationError):
            QueryExecuteRequest()


class TestQueryExecuteResponse:
    def test_valid_response(self):
        resp = QueryExecuteResponse(
            history_id=1,
            rows=[{"PATID": "P001", "SEX": "M"}, {"PATID": "P002", "SEX": "F"}],
            row_count=2,
            execution_ms=45,
        )
        assert resp.row_count == 2
        assert resp.execution_ms == 45

    def test_empty_rows(self):
        resp = QueryExecuteResponse(
            history_id=5,
            rows=[],
            row_count=0,
            execution_ms=12,
        )
        assert resp.rows == []
        assert resp.row_count == 0


class TestSavedQueryCreate:
    def test_valid_create(self):
        sq = SavedQueryCreate(name="Demographics Query", sql="SELECT * FROM DEMOGRAPHIC")
        assert sq.name == "Demographics Query"
        assert sq.description is None

    def test_with_description(self):
        sq = SavedQueryCreate(
            name="Encounter Count",
            description="Count of encounters by type",
            sql="SELECT ENC_TYPE, COUNT(*) FROM ENCOUNTER GROUP BY ENC_TYPE",
        )
        assert sq.description == "Count of encounters by type"

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            SavedQueryCreate(name="", sql="SELECT 1")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            SavedQueryCreate(name="x" * 256, sql="SELECT 1")

    def test_empty_sql_raises(self):
        with pytest.raises(ValidationError):
            SavedQueryCreate(name="Test", sql="")

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            SavedQueryCreate(sql="SELECT 1")


class TestSavedQueryUpdate:
    def test_all_optional(self):
        update = SavedQueryUpdate()
        assert update.name is None
        assert update.sql is None

    def test_partial_update_sql_only(self):
        update = SavedQueryUpdate(sql="SELECT PATID FROM DEMOGRAPHIC LIMIT 100")
        assert update.sql is not None
        assert update.name is None

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            SavedQueryUpdate(name="")


class TestSavedQueryResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = SavedQueryResponse(
            id=1,
            user_id=42,
            name="My Query",
            description=None,
            sql="SELECT * FROM DEMOGRAPHIC",
            created_at=now,
            updated_at=now,
        )
        assert resp.id == 1
        assert resp.user_id == 42


class TestQueryHistoryResponse:
    def test_valid_response_success(self):
        now = datetime.now(timezone.utc)
        resp = QueryHistoryResponse(
            id=1,
            user_id=1,
            sql="SELECT * FROM DEMOGRAPHIC",
            row_count=150,
            execution_ms=234,
            error=None,
            executed_at=now,
        )
        assert resp.row_count == 150
        assert resp.error is None

    def test_valid_response_with_error(self):
        now = datetime.now(timezone.utc)
        resp = QueryHistoryResponse(
            id=2,
            user_id=1,
            sql="SELECT * FROM NONEXISTENT_TABLE",
            row_count=None,
            execution_ms=12,
            error='relation "NONEXISTENT_TABLE" does not exist',
            executed_at=now,
        )
        assert resp.error is not None
        assert resp.row_count is None


class TestColumnInfo:
    def test_valid_column_info(self):
        col = ColumnInfo(name="PATID", type="character varying", nullable="NO")
        assert col.name == "PATID"
        assert col.type == "character varying"
        assert col.nullable == "NO"

    def test_nullable_column(self):
        col = ColumnInfo(name="BIRTH_DATE", type="character varying", nullable="YES")
        assert col.nullable == "YES"
