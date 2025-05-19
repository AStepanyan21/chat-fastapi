from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db_async
from app.dependencies.services import (
    get_chat_service,
    get_message_service,
    get_socket_event_service,
)
from app.models import Message, User
from app.repositories.user_repository import UserRepository
from app.schemas.base_event import WebSocketEvent
from app.schemas.message import MessageDTO, SendMessageRequest, SendMessageResponse
from app.schemas.ws_payloads import NewMessageNotificationPayload, NewMessagePayload
from app.services.chat_service import ChatService
from app.services.message_service import MessageService
from app.services.socket_event_service import SocketEventService
from app.ws.enums import WebSocketEventType

router = APIRouter(prefix="/messages", tags=["Message"])


@router.post(
    "/", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED
)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    chat_service: ChatService = Depends(get_chat_service),
    socket_service: SocketEventService = Depends(get_socket_event_service),
    db: AsyncSession = Depends(get_db_async),
):
    user_repo = UserRepository(db)

    target_user = None

    if request.chat_id:
        chat = await chat_service.get_by_id(request.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    elif request.target_user_id:
        target_user = await user_repo.get_by_id(request.target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")

        chat = await chat_service.get_or_create_private_chat(current_user, target_user)
    else:
        raise HTTPException(
            status_code=400, detail="chat_id or target_user_id required"
        )

    message = Message(
        chat_id=chat.id,
        sender_id=current_user.id,
        text=request.text,
        timestamp=datetime.now(UTC),
    )

    message = await message_service.create_message(message)

    await socket_service.send_chat_event_except_sender(
        chat_id=chat.id,
        sender_id=current_user.id,
        event=WebSocketEvent[NewMessagePayload](
            type=WebSocketEventType.NEW_MESSAGE,
            data=NewMessagePayload(
                message_id=str(message.id),
                chat_id=str(chat.id),
                sender_id=str(current_user.id),
                text=message.text,
                timestamp=message.timestamp,
            ),
        ),
    )

    if target_user:
        await socket_service.send_notification(
            user_id=target_user.id,
            event=WebSocketEvent[NewMessageNotificationPayload](
                type=WebSocketEventType.NEW_MESSAGE,
                data=NewMessageNotificationPayload(
                    chat_id=str(chat.id),
                    sender_name=current_user.name,
                    text=message.text,
                ),
            ),
        )

    return SendMessageResponse(message_id=message.id, chat_id=chat.id)


@router.get("/by-chat/{chat_id}", response_model=list[MessageDTO])
async def get_chat_messages(
    chat_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    chat_service: ChatService = Depends(get_chat_service),
):
    chat = await chat_service.get_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    has_access = await chat_service.has_access_to_chat(chat, current_user.id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = await message_service.get_chat_messages(chat_id, offset, limit)
    return messages
