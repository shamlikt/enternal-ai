import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import Role, User
from app.modules.agent.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    ChatMessageResponse,
    ChatSessionResponse,
)
from app.modules.agent.service import (
    get_session_messages,
    get_sessions,
    run_agent_query,
)

router = APIRouter()


@router.post("/query", response_model=AgentQueryResponse)
async def agent_query(
    request: AgentQueryRequest,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    result = await run_agent_query(db, current_user.id, request.question, request.session_id)
    return AgentQueryResponse(**result)


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await get_sessions(db, current_user.id)


@router.get("/sessions/{session_id}", response_model=list[ChatMessageResponse])
async def get_session_history(
    session_id: int,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    messages = await get_session_messages(db, session_id, current_user.id)
    if not messages and session_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return messages


@router.websocket("/ws")
async def agent_websocket(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for streaming agent responses.

    Clients send: {"token": "<jwt>", "question": "...", "session_id": null}
    Server streams: {"type": "token", "content": "..."} chunks, then {"type": "done", ...}
    """
    from app.core.security import decode_access_token
    from app.modules.auth.service import get_user_by_username

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            token = data.get("token")
            question = data.get("question", "")
            session_id = data.get("session_id")

            if not token or not question:
                await websocket.send_json({"type": "error", "content": "Missing token or question"})
                continue

            payload = decode_access_token(token)
            if not payload:
                await websocket.send_json({"type": "error", "content": "Invalid token"})
                continue

            user = await get_user_by_username(db, payload.get("sub", ""))
            if not user or not user.is_active or user.role not in (Role.ADMIN, Role.ANALYST):
                await websocket.send_json({"type": "error", "content": "Unauthorized"})
                continue

            await websocket.send_json({"type": "start"})
            try:
                result = await run_agent_query(db, user.id, question, session_id)
                await websocket.send_json({"type": "token", "content": result["answer"]})
                await websocket.send_json(
                    {
                        "type": "done",
                        "session_id": result["session_id"],
                        "message_id": result["message_id"],
                        "sql_generated": result.get("sql_generated"),
                        "row_count": len(result.get("rows") or []),
                    }
                )
            except Exception as exc:
                await websocket.send_json({"type": "error", "content": str(exc)})

    except WebSocketDisconnect:
        pass
