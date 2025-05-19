from typing import Generic, TypeVar

from pydantic import BaseModel

from app.ws.enums import WebSocketEventType

T = TypeVar("T")


class WebSocketEvent(BaseModel, Generic[T]):
    type: WebSocketEventType
    data: T
