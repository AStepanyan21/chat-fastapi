import logging.config

from fastapi import FastAPI, HTTPException

from app.api import group_router, message_router, user_router
from app.core.error_handler import (
    ErrorLoggingMiddleware,
    http_exception_handler,
)
from app.core.log_config import LOGGING_CONFIG
from app.ws.chat_ws import router as chat_ws_router
from app.ws.notifications_ws import router as notifications_ws_router

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")
app = FastAPI()

app.add_middleware(ErrorLoggingMiddleware)
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(user_router)
app.include_router(message_router)
app.include_router(group_router)
app.include_router(chat_ws_router)
app.include_router(notifications_ws_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=LOGGING_CONFIG,
    )
