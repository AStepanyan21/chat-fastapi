from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chat, User
from app.models.chat import ChatType
from app.models.group import Group
from app.repositories.chat_repository import ChatRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.user import UserRead


class GroupService:
    def __init__(self, db: AsyncSession):
        self.repo = GroupRepository(db)
        self.chat_repo = ChatRepository(db)

    async def get_by_id(self, group_id: UUID) -> Group | None:
        return await self.repo.get_by_id(group_id)

    async def create_group(self, name: str, owner: User) -> Group:
        chat = Chat(name=name, type=ChatType.public)
        chat = await self.chat_repo.create(chat)

        group = Group(name=name, owner_id=owner.id, chat_id=chat.id)
        group = await self.repo.create(group)

        await self.repo.add_member(group.id, owner.id)

        return group

    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        if await self.repo.is_member(group_id, user_id):
            return
        await self.repo.add_member(group_id, user_id)

    async def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        group = await self.repo.get_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        if group.owner_id == user_id:
            raise ValueError("Owner cannot be removed from group")
        await self.repo.remove_member(group_id, user_id)

    async def list_members(
        self, group_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[UserRead]:
        return await self.repo.list_members(group_id, offset=offset, limit=limit)

    async def list_members_id(
        self, group_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[UUID]:
        return await self.repo.list_members_id(group_id, offset=offset, limit=limit)

    async def list_user_groups(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[Group]:
        return await self.repo.list_user_groups(user_id, offset=offset, limit=limit)

    async def get_by_chat_id(self, chat_id: UUID) -> Group | None:
        return await self.repo.get_by_chat_id(chat_id)
