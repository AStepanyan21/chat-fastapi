from uuid import UUID

from app.dependencies.services import get_message_service
from app.infrastructure.jwt_service import UserTokenPayload
from app.schemas.base_event import WebSocketEvent
from app.schemas.ws_payloads import MessageReadRequest

message_service = get_message_service()


async def handle_read(
    raw_event: WebSocketEvent,
    user: UserTokenPayload,
):
    event = WebSocketEvent[MessageReadRequest](**raw_event.dict())

    await message_service.mark_as_read(
        message_id=event.data.message_id, user_id=UUID(user.sub)
    )
