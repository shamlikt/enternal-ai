"""
Unit tests for app.modules.agent.service and app.modules.agent.schemas.

Tests cover:
- Agent schema validation (AgentQueryRequest, AgentQueryResponse, ChatSessionResponse,
  ChatMessageResponse)
- get_or_create_session: returns existing session, creates new when none found,
  creates new when session_id is None
- get_sessions: returns ordered list of sessions
- get_session_messages: returns [] for unowned session, returns messages for owned session
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.modules.agent.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    ChatMessageResponse,
    ChatSessionResponse,
)
from app.modules.agent.service import (
    get_or_create_session,
    get_session_messages,
    get_sessions,
)
from app.modules.agent.models import ChatSession, ChatMessage


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestAgentQueryRequest:
    def test_valid_request(self):
        req = AgentQueryRequest(question="How many patients are there?")
        assert req.question == "How many patients are there?"
        assert req.session_id is None

    def test_with_session_id(self):
        req = AgentQueryRequest(question="Count encounters", session_id=42)
        assert req.session_id == 42

    def test_missing_question_raises(self):
        with pytest.raises(ValidationError):
            AgentQueryRequest()


class TestAgentQueryResponse:
    def test_valid_response(self):
        resp = AgentQueryResponse(
            session_id=1,
            message_id=5,
            answer="There are 1500 patients.",
            sql_generated="SELECT COUNT(*) FROM DEMOGRAPHIC",
            rows=[{"count": 1500}],
        )
        assert resp.session_id == 1
        assert resp.message_id == 5
        assert resp.sql_generated is not None
        assert resp.rows is not None

    def test_optional_fields_default_to_none(self):
        resp = AgentQueryResponse(
            session_id=2,
            message_id=10,
            answer="I could not generate a response.",
        )
        assert resp.sql_generated is None
        assert resp.rows is None

    def test_missing_required_fields_raises(self):
        with pytest.raises(ValidationError):
            AgentQueryResponse(answer="Some answer")


class TestChatSessionResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = ChatSessionResponse(
            id=1,
            user_id=10,
            title="Patient count query",
            created_at=now,
            updated_at=now,
        )
        assert resp.id == 1
        assert resp.title == "Patient count query"

    def test_none_title_allowed(self):
        now = datetime.now(timezone.utc)
        resp = ChatSessionResponse(
            id=2,
            user_id=10,
            title=None,
            created_at=now,
            updated_at=now,
        )
        assert resp.title is None


class TestChatMessageResponse:
    def test_valid_assistant_message(self):
        now = datetime.now(timezone.utc)
        resp = ChatMessageResponse(
            id=1,
            session_id=5,
            role="assistant",
            content="There are 1500 patients.",
            sql_generated="SELECT COUNT(*) FROM DEMOGRAPHIC",
            result_json='[{"count": 1500}]',
            created_at=now,
        )
        assert resp.role == "assistant"
        assert resp.sql_generated is not None

    def test_user_message_no_sql(self):
        now = datetime.now(timezone.utc)
        resp = ChatMessageResponse(
            id=2,
            session_id=5,
            role="user",
            content="How many patients are there?",
            sql_generated=None,
            result_json=None,
            created_at=now,
        )
        assert resp.role == "user"
        assert resp.sql_generated is None
        assert resp.result_json is None


# ---------------------------------------------------------------------------
# Service tests with mocked DB
# ---------------------------------------------------------------------------


def _make_session(session_id: int = 1, user_id: int = 1, title: str = "Test") -> ChatSession:
    s = ChatSession()
    s.id = session_id
    s.user_id = user_id
    s.title = title
    s.created_at = datetime.now(timezone.utc)
    s.updated_at = datetime.now(timezone.utc)
    return s


def _make_message(
    msg_id: int = 1,
    session_id: int = 1,
    role: str = "user",
    content: str = "Hello",
) -> ChatMessage:
    m = ChatMessage()
    m.id = msg_id
    m.session_id = session_id
    m.role = role
    m.content = content
    m.sql_generated = None
    m.result_json = None
    m.created_at = datetime.now(timezone.utc)
    return m


class TestGetOrCreateSession:
    @pytest.mark.asyncio
    async def test_returns_existing_session_when_found(self):
        existing = _make_session(session_id=7, user_id=1)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing

        db = AsyncMock()
        db.execute.return_value = result_mock
        db.flush = AsyncMock()

        session = await get_or_create_session(db, user_id=1, session_id=7, first_question="Hi")
        assert session is existing
        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_new_session_when_not_found(self):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None

        db = AsyncMock()
        db.execute.return_value = result_mock
        db.flush = AsyncMock()

        session = await get_or_create_session(
            db, user_id=2, session_id=99, first_question="How many encounters?"
        )
        db.add.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.user_id == 2
        assert "How many encounters?" in added.title

    @pytest.mark.asyncio
    async def test_creates_new_session_when_session_id_is_none(self):
        db = AsyncMock()
        db.flush = AsyncMock()

        session = await get_or_create_session(
            db, user_id=3, session_id=None, first_question="Count patients"
        )
        db.add.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.user_id == 3
        # Title should be first 100 chars of the question
        assert added.title == "Count patients"

    @pytest.mark.asyncio
    async def test_title_is_truncated_to_100_chars(self):
        db = AsyncMock()
        db.flush = AsyncMock()

        long_question = "x" * 200
        await get_or_create_session(db, user_id=1, session_id=None, first_question=long_question)
        added = db.add.call_args[0][0]
        assert len(added.title) == 100

    @pytest.mark.asyncio
    async def test_empty_question_uses_default_title(self):
        db = AsyncMock()
        db.flush = AsyncMock()

        await get_or_create_session(db, user_id=1, session_id=None, first_question="")
        added = db.add.call_args[0][0]
        assert added.title == "New Chat"


class TestGetSessions:
    @pytest.mark.asyncio
    async def test_returns_list_of_sessions(self):
        s1 = _make_session(session_id=1, user_id=5)
        s2 = _make_session(session_id=2, user_id=5)

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [s2, s1]

        db = AsyncMock()
        db.execute.return_value = result_mock

        sessions = await get_sessions(db, user_id=5)
        assert len(sessions) == 2
        assert sessions[0].id == 2  # most recent first

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_sessions(self):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []

        db = AsyncMock()
        db.execute.return_value = result_mock

        sessions = await get_sessions(db, user_id=99)
        assert sessions == []


class TestGetSessionMessages:
    @pytest.mark.asyncio
    async def test_returns_empty_when_session_not_owned(self):
        """If user doesn't own the session, returns empty list."""
        session_result = MagicMock()
        session_result.scalar_one_or_none.return_value = None

        db = AsyncMock()
        db.execute.return_value = session_result

        messages = await get_session_messages(db, session_id=1, user_id=999)
        assert messages == []

    @pytest.mark.asyncio
    async def test_returns_messages_for_owned_session(self):
        session = _make_session(session_id=1, user_id=1)
        m1 = _make_message(msg_id=1, session_id=1, role="user", content="Hello")
        m2 = _make_message(msg_id=2, session_id=1, role="assistant", content="Hi there")

        session_result = MagicMock()
        session_result.scalar_one_or_none.return_value = session

        messages_result = MagicMock()
        messages_result.scalars.return_value.all.return_value = [m1, m2]

        db = AsyncMock()
        db.execute.side_effect = [session_result, messages_result]

        messages = await get_session_messages(db, session_id=1, user_id=1)
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
