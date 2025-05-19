import logging
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from app.schemas.base_event import WebSocketEvent
from app.ws.managers.chat_manager import ChatManager
from app.ws.managers.notification_manager import NotificationManager

logger = logging.getLogger("app")


class SocketEventService:
    def __init__(
        self,
        chat_manager: ChatManager,
        notification_manager: NotificationManager,
    ):
        self.chat_manager = chat_manager
        self.notification_manager = notification_manager

    async def send_chat_event(self, chat_id: UUID, event: WebSocketEvent):
        await self.chat_manager.send_to_chat(str(chat_id), event.model_dump())

    async def send_chat_event_except_sender(
        self, chat_id: UUID, sender_id: UUID, event: WebSocketEvent
    ):
        try:
            await self.chat_manager.send_to_others(
                str(chat_id), str(sender_id), jsonable_encoder(event)
            )
        except Exception as e:
            logger.exception(e)

    async def send_notification(self, user_id: UUID, event: WebSocketEvent):
        await self.notification_manager.send_to_user(str(user_id), event.model_dump())

    async def send_to_users(self, user_ids: list[UUID], event: WebSocketEvent):
        for user_id in user_ids:
            await self.send_notification(user_id, event)
