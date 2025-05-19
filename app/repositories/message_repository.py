from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models import User
from app.models.group import Group
from app.models.message import Message
from app.models.message_reads import MessageRead
from app.schemas.message import MessageDTO


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, message_id: UUID) -> Message | None:
        result = await self.db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    async def create(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.flush()
        return message

    async def get_by_chat_id(
        self, chat_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_dtos_by_chat_id(
        self, chat_id: UUID, offset=0, limit=20
    ) -> list[MessageDTO]:
        u = aliased(User)

        stmt = (
            select(
                Message.id.label("id"),
                Message.chat_id.label("chat_id"),
                u.name.label("sender_name"),
                Message.text.label("text"),
                Message.timestamp.label("timestamp"),
                Message.is_readed.label("is_readed"),
            )
            .join(u, u.id == Message.sender_id)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.mappings().all()

        return [MessageDTO.model_validate(row) for row in rows]

    async def get_by_group_id(
        self, group_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[Message]:
        result = await self.db.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()
        if not group:
            return []
        return await self.get_by_chat_id(group.chat_id, offset, limit)

    async def has_user_read(self, message_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(MessageRead).where(
                MessageRead.message_id == message_id, MessageRead.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def save_read_status(self, message_id: UUID, user_id: UUID):
        self.db.add(MessageRead(message_id=message_id, user_id=user_id))
        await self.db.commit()

    async def get_readers(self, message_id: UUID) -> list[UUID]:
        result = await self.db.execute(
            select(MessageRead.user_id).where(MessageRead.message_id == message_id)
        )
        return [row[0] for row in result.all()]

    async def is_duplicate_message(
        self,
        chat_id: UUID,
        sender_id: UUID,
        text: str,
        timestamp: datetime,
        threshold_seconds: int = 2,
    ) -> bool:
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .where(Message.sender_id == sender_id)
            .where(Message.text == text)
            .where(
                Message.timestamp.between(
                    timestamp - timedelta(seconds=threshold_seconds),
                    timestamp + timedelta(seconds=threshold_seconds),
                )
            )
        )
        return result.scalar_one_or_none() is not None
