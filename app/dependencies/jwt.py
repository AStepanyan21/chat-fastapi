from app.infrastructure.jwt_service import JWTService


def get_jwt_service() -> JWTService:
    return JWTService()
