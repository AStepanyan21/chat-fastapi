import pytest

from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_success(db_session):
    service = UserService(db_session)
    user_data = UserCreate(name="Test", email="test@example.com", password="secret")

    user = await service.register(user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.password != "secret"


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session):
    service = UserService(db_session)
    user_data = UserCreate(name="User", email="dupe@example.com", password="pw")

    await service.register(user_data)

    with pytest.raises(ValueError, match="Email already in use"):
        await service.register(user_data)


@pytest.mark.asyncio
async def test_authenticate_success(db_session):
    service = UserService(db_session)
    user_data = UserCreate(name="Auth", email="auth@example.com", password="mypassword")

    created = await service.register(user_data)

    user = await service.authenticate("auth@example.com", "mypassword")
    assert user is not None
    assert user.id == created.id


@pytest.mark.asyncio
async def test_authenticate_wrong_password(db_session):
    service = UserService(db_session)
    user_data = UserCreate(
        name="WrongPW", email="wrongpw@example.com", password="rightpass"
    )
    await service.register(user_data)

    user = await service.authenticate("wrongpw@example.com", "wrongpass")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_unknown_email(db_session):
    service = UserService(db_session)
    user = await service.authenticate("notfound@example.com", "pw")
    assert user is None


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    service = UserService(db_session)
    user_data = UserCreate(name="ById", email="byid@example.com", password="pw")
    user = await service.register(user_data)

    result = await service.get_by_id(user.id)
    assert result is not None
    assert result.id == user.id
