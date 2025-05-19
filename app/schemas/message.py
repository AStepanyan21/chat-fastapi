from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    chat_id: Optional[UUID] = None
    target_user_id: Optional[UUID] = None
    text: str = Field(..., min_length=1)


class SendMessageResponse(BaseModel):
    message_id: UUID
    chat_id: UUID


class MessageDTO(BaseModel):
    id: UUID
    chat_id: UUID
    sender_name: str
    text: str
    timestamp: datetime
    is_readed: bool


class MessageReadStatusPayload(BaseModel):
    message_id: UUID
