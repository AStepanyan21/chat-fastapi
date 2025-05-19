from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db_async
from app.dependencies.jwt import get_jwt_service
from app.dependencies.services import get_user_service
from app.infrastructure.jwt_service import JWTService, UserTokenPayload
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=TokenResponse)
async def register_user(
    user: UserCreate,
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_user_service),
):
    try:
        created_user = await user_service.register(user)
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    payload = UserTokenPayload(sub=str(created_user.id), name=created_user.name)
    token = jwt_service.create_token(payload)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login_user(
    data: LoginRequest,
    db=Depends(get_db_async),
    jwt_service: JWTService = Depends(get_jwt_service),
):
    service = UserService(db)
    user = await service.authenticate(email=data.email, password=data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    payload = UserTokenPayload(sub=str(user.id), name=user.name)
    token = jwt_service.create_token(payload)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user=Depends(get_current_user)):
    return current_user
