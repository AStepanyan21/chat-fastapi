from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db_async
from app.dependencies.websockets import get_chat_manager, get_notification_manager
from app.services.chat_service import ChatService
from app.services.group_service import GroupService
from app.services.message_service import MessageService
from app.services.socket_event_service import SocketEventService
from app.services.user_service import UserService


def get_chat_service(db: AsyncSession = Depends(get_db_async)) -> ChatService:
    return ChatService(db)


def get_group_service(db: AsyncSession = Depends(get_db_async)) -> GroupService:
    return GroupService(db)


def get_socket_event_service() -> SocketEventService:
    return SocketEventService(
        chat_manager=get_chat_manager(),
        notification_manager=get_notification_manager(),
    )


def get_message_service(
    db: AsyncSession = Depends(get_db_async),
    group_service: GroupService = Depends(get_group_service),
    socket_service: SocketEventService = Depends(get_socket_event_service),
) -> MessageService:
    return MessageService(db, group_service, socket_service)


def get_user_service(db: AsyncSession = Depends(get_db_async)) -> UserService:
    return UserService(db)
