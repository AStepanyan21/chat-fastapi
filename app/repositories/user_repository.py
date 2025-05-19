from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID | str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_name(self, user_id: UUID, new_name: str) -> bool:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(name=new_name)
            .returning(User.id)
        )
        await self.db.commit()
        return result.scalar() is not None

    async def update_password(self, user_id: UUID, new_password: str) -> bool:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password=new_password)
            .returning(User.id)
        )
        await self.db.commit()
        return result.scalar() is not None
