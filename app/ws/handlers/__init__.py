from typing import Awaitable, Callable

from app.infrastructure.jwt_service import UserTokenPayload
from app.schemas.base_event import WebSocketEvent
from app.ws.enums import WebSocketEventType
from app.ws.handlers.socket_event_handlers import handle_read

SocketHandler = Callable[[WebSocketEvent, UserTokenPayload], Awaitable[None]]
event_handlers: dict[WebSocketEventType, SocketHandler] = {
    WebSocketEventType.READ: handle_read,
}
