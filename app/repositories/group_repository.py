from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group, group_members
from app.schemas.user import UserRead


class GroupRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, group_id: UUID) -> Group | None:
        result = await self.db.execute(select(Group).where(Group.id == group_id))
        return result.scalar_one_or_none()

    async def create(self, group: Group) -> Group:
        self.db.add(group)
        await self.db.flush()
        return group

    async def add_member(self, group_id: UUID, user_id: UUID):
        await self.db.execute(
            group_members.insert().values(group_id=group_id, user_id=user_id)
        )

    async def remove_member(self, group_id: UUID, user_id: UUID):
        await self.db.execute(
            group_members.delete().where(
                group_members.c.group_id == group_id, group_members.c.user_id == user_id
            )
        )

    async def is_member(self, group_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(group_members).where(
                group_members.c.group_id == group_id, group_members.c.user_id == user_id
            )
        )
        return result.first() is not None

    async def list_members(
        self, group_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[UserRead]:
        result = await self.db.execute(
            select(group_members.c.user_id)
            .where(group_members.c.group_id == group_id)
            .offset(offset)
            .limit(limit)
        )
        return result.all()

    async def list_members_id(
        self, group_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[UUID]:
        result = await self.db.execute(
            select(group_members.c.user_id)
            .where(group_members.c.group_id == group_id)
            .offset(offset)
            .limit(limit)
        )
        return [row[0] for row in result.all()]

    async def list_user_groups(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[Group]:
        result = await self.db.execute(
            select(Group)
            .join(group_members)
            .where(group_members.c.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def is_user_in_group_by_chat(self, chat_id: UUID, user_id: UUID) -> bool:
        stmt = (
            select(Group.id)
            .join(group_members, Group.id == group_members.c.group_id)
            .where(Group.chat_id == chat_id)
            .where(group_members.c.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_chat_id(self, chat_id: UUID) -> Group | None:
        result = await self.db.execute(select(Group).where(Group.chat_id == chat_id))
        return result.scalar_one_or_none()
