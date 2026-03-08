import json
from typing import Any, Optional

from langchain_core.messages import HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agent.bedrock_adapter import BedrockAdapter
from app.modules.agent.graph import create_agent_graph
from app.modules.agent.models import ChatMessage, ChatSession
from app.modules.query.postgres_adapter import PostgresAdapter
from app.modules.query.service import _validate_select_only


async def _build_schema_context(db: AsyncSession) -> str:
    adapter = PostgresAdapter(db)
    try:
        tables = await adapter.get_tables()
        lines = []
        for table in tables[:30]:  # limit to avoid huge prompts
            cols = await adapter.get_columns(table)
            col_str = ", ".join(f"{c['name']} ({c['type']})" for c in cols[:20])
            lines.append(f"- {table}: {col_str}")
        return "\n".join(lines)
    except Exception:
        return "Schema not available"


async def get_or_create_session(
    db: AsyncSession, user_id: int, session_id: Optional[int], first_question: str
) -> ChatSession:
    if session_id:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if session:
            return session
    # Create new session with title from first question
    title = first_question[:100] if first_question else "New Chat"
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    return session


async def run_agent_query(
    db: AsyncSession,
    user_id: int,
    question: str,
    session_id: Optional[int],
) -> dict[str, Any]:
    session = await get_or_create_session(db, user_id, session_id, question)

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=question)
    db.add(user_msg)
    await db.flush()

    schema_context = await _build_schema_context(db)
    adapter_instance = BedrockAdapter()
    llm = adapter_instance.get_chat_model()

    # Build execute function for the agent
    async def execute_fn(sql: str):
        _validate_select_only(sql)
        pg = PostgresAdapter(db)
        return await pg.execute_query(sql)

    graph = create_agent_graph(llm, schema_context)
    result = await graph.ainvoke(
        {
            "messages": [HumanMessage(content=question)],
            "sql_generated": None,
            "query_results": None,
            "execute_fn": execute_fn,
        }
    )

    last_ai = None
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and not hasattr(msg, "tool_calls"):
            last_ai = msg
            break

    answer = last_ai.content if last_ai else "I could not generate a response."
    sql_generated = result.get("sql_generated")
    query_results = result.get("query_results")

    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
        sql_generated=sql_generated,
        result_json=json.dumps(query_results, default=str) if query_results else None,
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)
    await db.refresh(session)

    return {
        "session_id": session.id,
        "message_id": assistant_msg.id,
        "answer": answer,
        "sql_generated": sql_generated,
        "rows": query_results,
    }


async def get_sessions(db: AsyncSession, user_id: int) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_session_messages(db: AsyncSession, session_id: int, user_id: int) -> list[ChatMessage]:
    # verify ownership
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return []
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())
