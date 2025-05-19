from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from app.schemas.base_event import WebSocketEvent
from app.schemas.message import MessageDTO, MessageReadStatusPayload
from app.services.group_service import GroupService
from app.services.socket_event_service import SocketEventService
from app.ws.enums import WebSocketEventType


class MessageService:
    def __init__(
        self,
        db: AsyncSession,
        group_service: GroupService,
        socket_service: SocketEventService,
    ):
        self.repo = MessageRepository(db)
        self.group_service = group_service
        self.socket_service = socket_service

    async def get_by_id(self, message_id: UUID) -> Message | None:
        return await self.repo.get_by_id(message_id)

    async def create_message(self, message: Message) -> Message:
        if await self.repo.is_duplicate_message(
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            text=message.text,
            timestamp=message.timestamp,
        ):
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Duplicate message detected",
            )
        return await self.repo.create(message)

    async def get_chat_messages(
        self, chat_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[MessageDTO]:
        return await self.repo.get_dtos_by_chat_id(chat_id, offset, limit)

    async def get_group_messages(
        self, group_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[Message]:
        return await self.repo.get_by_group_id(group_id, offset, limit)

    async def mark_as_read(self, message_id: UUID, user_id: UUID):
        if await self.repo.has_user_read(message_id, user_id):
            return

        await self.repo.save_read_status(message_id, user_id)

        message = await self.repo.get_by_id(message_id)
        if not message:
            return

        group = await self.group_service.get_by_chat_id(message.chat_id)

        if group:
            member_ids = await self.group_service.list_members_id(group.id)
            readers = await self.repo.get_readers(message_id)

            member_ids = [UUID(m) if isinstance(m, str) else m for m in member_ids]
            readers = [UUID(r) if isinstance(r, str) else r for r in readers]

            if set(member_ids).issubset(set(readers)):
                await self.socket_service.send_notification(
                    user_id=message.sender_id,
                    event=WebSocketEvent[MessageReadStatusPayload](
                        type=WebSocketEventType.MESSAGE_READ_BY_ALL,
                        data=MessageReadStatusPayload(message_id=message.id),
                    ),
                )
        else:
            await self.socket_service.send_notification(
                user_id=message.sender_id,
                event=WebSocketEvent[MessageReadStatusPayload](
                    type=WebSocketEventType.MESSAGE_READ,
                    data=MessageReadStatusPayload(message_id=message.id),
                ),
            )
