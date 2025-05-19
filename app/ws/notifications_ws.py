import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.dependencies.jwt import get_jwt_service
from app.dependencies.websockets import get_notification_manager
from app.infrastructure.jwt_service import JWTService, UserTokenPayload
from app.ws.managers.notification_manager import NotificationManager

router = APIRouter()
logger = logging.getLogger("app")


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    jwt_service: JWTService = Depends(get_jwt_service),
    manager: NotificationManager = Depends(get_notification_manager),
):
    token = websocket.query_params.get("token")
    user_id: str | None = None

    try:
        user_data: UserTokenPayload = jwt_service.verify_token(token)
        await manager.connect(user_data.sub, websocket)

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
            logger.info(f"WebSocket disconnected: user_id={user_id}")

    except Exception as e:
        logger.exception(f"WebSocket error : {e}")

        await websocket.close(code=1008)
