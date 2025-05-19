from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.schemas.base_event import WebSocketEvent
from app.schemas.ws_payloads import ChatCreatedPayload
from app.services.socket_event_service import SocketEventService
from app.ws.enums import WebSocketEventType


@pytest.mark.asyncio
async def test_send_chat_event_calls_chat_manager():
    chat_manager = AsyncMock()
    notification_manager = AsyncMock()

    service = SocketEventService(
        chat_manager=chat_manager, notification_manager=notification_manager
    )

    chat_id = uuid4()
    payload = ChatCreatedPayload(chat_id=str(chat_id), inviter_name="Alice")
    event = WebSocketEvent[ChatCreatedPayload](
        type=WebSocketEventType.CHAT_CREATED, data=payload
    )

    await service.send_chat_event(chat_id, event)
    chat_manager.send_to_chat.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_notification_calls_notification_manager():
    chat_manager = AsyncMock()
    notification_manager = AsyncMock()

    service = SocketEventService(chat_manager, notification_manager)

    user_id = uuid4()
    event = WebSocketEvent(
        type=WebSocketEventType.CHAT_CREATED,
        data={"chat_id": str(uuid4()), "inviter_name": "X"},
    )

    await service.send_notification(user_id, event)
    notification_manager.send_to_user.assert_awaited_once()
