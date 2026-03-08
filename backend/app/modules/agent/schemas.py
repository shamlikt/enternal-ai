from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class AgentQueryRequest(BaseModel):
    question: str
    session_id: Optional[int] = None


class AgentQueryResponse(BaseModel):
    session_id: int
    message_id: int
    answer: str
    sql_generated: Optional[str] = None
    rows: Optional[list[dict[str, Any]]] = None


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    sql_generated: Optional[str]
    result_json: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
