from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> User:
        user_data.email = user_data.email.lower()
        existing = await self.repo.get_by_email(user_data.email)
        if existing:
            raise ValueError("Email already in use")

        hashed_pw = self._hash_password(user_data.password)
        user_data.password = hashed_pw
        return await self.repo.create(user_data)

    async def authenticate(self, email: str, password: str) -> User | None:
        email = email.lower()
        user = await self.repo.get_by_email(email)
        if not user:
            return None

        if not self._verify_password(password, user.password):
            return None

        return user

    async def get_by_id(self, user_id) -> User | None:
        return await self.repo.get_by_id(user_id)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
