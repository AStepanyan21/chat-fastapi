from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.chat import Chat, ChatType
from app.repositories.chat_repository import ChatRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.chat import ChatResponseDTO


class ChatService:
    def __init__(self, db: AsyncSession):
        self.repo = ChatRepository(db)
        self.group_repo = GroupRepository(db)

    async def get_by_id(self, chat_id: UUID) -> Chat | None:
        return await self.repo.get_by_id(chat_id)

    async def list_all(self, offset: int = 0, limit: int = 20) -> list[Chat]:
        return await self.repo.list_all(offset=offset, limit=limit)

    async def get_or_create_private_chat(self, user1: User, user2: User) -> Chat:
        chat = await self.repo.get_private_chat_between_users(user1.id, user2.id)
        if chat:
            return chat

        new_chat = Chat(name=f"{user1.name}_{user2.name}", type=ChatType.private)
        created_chat = await self.repo.create(new_chat)
        return created_chat

    async def get_user_private_chats(
        self, user_id: UUID, offset=0, limit=20
    ) -> list[Chat]:
        return await self.repo.get_user_private_chats(user_id, offset, limit)

    async def get_all_user_chats(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[ChatResponseDTO]:
        private_chats = await self.repo.get_user_private_chats(user_id)
        user_groups = await self.group_repo.list_user_groups(user_id)
        group_chat_ids = [group.chat_id for group in user_groups if group.chat_id]

        group_chats = await self.repo.get_by_ids(group_chat_ids)

        all_chats = private_chats + group_chats

        dtos: list[ChatResponseDTO] = []
        for chat in all_chats:
            dto = await self.repo.chat_to_dto(chat)
            dtos.append(dto)

        dtos = sorted(
            dtos, key=lambda c: c.last_message_timestamp or datetime.min, reverse=True
        )

        return dtos[offset : offset + limit]

    async def has_access_to_chat(self, chat: Chat, user_id: UUID | str) -> bool:
        if chat.type == ChatType.private:
            return await self.repo.is_user_in_private_chat(chat.id, user_id)
        elif chat.type == ChatType.public:
            return await self.group_repo.is_user_in_group_by_chat(chat.id, user_id)
        return False
