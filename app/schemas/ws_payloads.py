from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatCreatedPayload(BaseModel):
    chat_id: str
    inviter_name: str


class NewMessageNotificationPayload(BaseModel):
    chat_id: str
    sender_name: str
    text: str


class NewMessagePayload(BaseModel):
    message_id: str
    chat_id: str
    sender_id: str
    text: str
    timestamp: datetime


class MessageReadRequest(BaseModel):
    message_id: UUID


class TypingEventPayload(BaseModel):
    chat_id: UUID
    is_typing: bool
