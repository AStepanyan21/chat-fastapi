import logging
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.dependencies.jwt import get_jwt_service
from app.dependencies.websockets import get_chat_manager
from app.infrastructure.jwt_service import JWTService, UserTokenPayload
from app.schemas.base_event import WebSocketEvent
from app.ws.handlers import event_handlers
from app.ws.managers.chat_manager import ChatManager

router = APIRouter()
logger = logging.getLogger("app")


@router.websocket("/ws/chat/{chat_id}")
async def websocket_chat(
    chat_id: UUID,
    websocket: WebSocket,
    jwt_service: JWTService = Depends(get_jwt_service),
    manager: ChatManager = Depends(get_chat_manager),
):
    token = websocket.query_params.get("token")
    user_id: str | None = None

    try:
        user_data: UserTokenPayload = jwt_service.verify_token(token)
        user_id = user_data.sub
        await manager.connect(str(chat_id), user_id, websocket)

        while True:
            raw = await websocket.receive_json()
            base_event = WebSocketEvent[dict](**raw)

            handler = event_handlers.get(base_event.type)
            if handler:
                await handler(
                    raw,
                    user_data,
                )
            else:
                logger.warning(f"Unknown WebSocket event type: {base_event.type}")

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(str(chat_id), user_id)
            logger.info(f"WebSocket disconnected: chat_id={chat_id}, user_id={user_id}")

    except Exception as e:
        logger.exception(f"WebSocket error: chat_id={chat_id}, error={e}")
        await websocket.close(code=1008)
