from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies.db import get_db_async
from app.infrastructure.jwt_service import JWTService
from app.models import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = HTTPBearer()


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db=Depends(get_db_async),
) -> User:
    jwt_service: JWTService = JWTService()
    try:
        payload = jwt_service.verify_token(token.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
