from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat, ChatType
from app.models.message import Message
from app.schemas.chat import ChatResponseDTO


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, chat_id: UUID) -> Chat | None:
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def create(self, chat: Chat) -> Chat:
        self.db.add(chat)
        await self.db.flush()
        return chat

    async def list_all(self, offset: int = 0, limit: int = 20) -> list[Chat]:
        result = await self.db.execute(select(Chat).offset(offset).limit(limit))
        return result.scalars().all()

    async def get_private_chat_between_users(
        self, user1_id: UUID, user2_id: UUID
    ) -> Chat | None:
        stmt = (
            select(Chat)
            .join(Message, Message.chat_id == Chat.id)
            .where(
                Chat.type == ChatType.private.value,
                Message.sender_id.in_([user1_id, user2_id]),
            )
            .group_by(Chat.id)
            .having(func.count(func.distinct(Message.sender_id)) >= 1)
            .order_by(func.count(func.distinct(Message.sender_id)).desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_private_chats(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[Chat]:
        stmt = (
            select(Chat)
            .join(Message, Message.chat_id == Chat.id)
            .where(Chat.type == ChatType.private.value, Message.sender_id == user_id)
            .group_by(Chat.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(self, ids: list[UUID]) -> list[Chat]:
        if not ids:
            return []
        result = await self.db.execute(select(Chat).where(Chat.id.in_(ids)))
        return result.scalars().all()

    async def chat_to_dto(self, chat: Chat) -> ChatResponseDTO:
        result = await self.db.execute(
            select(Message.timestamp)
            .where(Message.chat_id == chat.id)
            .order_by(Message.timestamp.desc())
            .limit(1)
        )
        last_ts = result.scalar_one_or_none()

        return ChatResponseDTO(
            id=chat.id,
            name=chat.name,
            type=chat.type.value,
            last_message_timestamp=last_ts,
        )

    async def is_user_in_private_chat(self, chat_id: UUID, user_id: UUID) -> bool:
        stmt = select(
            exists().where(Message.chat_id == chat_id, Message.sender_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar()
