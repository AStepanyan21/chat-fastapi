import os
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from pydantic import BaseModel


class UserTokenPayload(BaseModel):
    sub: str
    name: str


class JWTService:
    def __init__(self) -> None:
        self.secret = os.getenv("JWT_SECRET", "dev-secret")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.expires_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

    def create_token(self, payload: UserTokenPayload) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.expires_minutes)
        token_payload = payload.model_dump()
        token_payload["exp"] = expire
        return jwt.encode(token_payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> UserTokenPayload:
        try:
            data = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return UserTokenPayload(**data)
        except JWTError:
            raise ValueError("Invalid token")
