import pytest
from jose import jwt

from app.infrastructure.jwt_service import JWTService, UserTokenPayload


@pytest.fixture
def jwt_service():
    return JWTService()


@pytest.fixture
def sample_payload():
    return UserTokenPayload(sub="user-id", name="Test User")


def test_create_token(jwt_service, sample_payload):
    token = jwt_service.create_token(sample_payload)
    assert isinstance(token, str)

    decoded = jwt.decode(token, jwt_service.secret, algorithms=[jwt_service.algorithm])
    assert decoded["sub"] == sample_payload.sub
    assert decoded["name"] == sample_payload.name
    assert "exp" in decoded


def test_verify_token_valid(jwt_service, sample_payload):
    token = jwt_service.create_token(sample_payload)
    payload = jwt_service.verify_token(token)
    assert isinstance(payload, UserTokenPayload)
    assert payload.sub == sample_payload.sub
    assert payload.name == sample_payload.name


def test_verify_token_invalid(jwt_service):
    with pytest.raises(ValueError, match="Invalid token"):
        jwt_service.verify_token("invalid.token.here")
