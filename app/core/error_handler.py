import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_400_BAD_REQUEST

logger = logging.getLogger("app")


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except Exception as e:
            logger.exception(f"Unhandled error on {request.url}: {str(e)}")
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"message": "Something went wrong"},
            )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException: {exc.detail} [{exc.status_code}] on {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
