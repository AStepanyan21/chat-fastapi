from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ChatResponseDTO(BaseModel):
    id: UUID
    name: str
    type: Literal["private", "public"]
    last_message_timestamp: datetime | None = None


class StartPrivateChatRequest(BaseModel):
    user_id: UUID


class StartPrivateChatResponse(BaseModel):
    chat_id: UUID
