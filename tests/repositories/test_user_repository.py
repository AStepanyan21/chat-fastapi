import pytest

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_and_get_by_id(db_session):
    repo = UserRepository(db_session)

    user_data = UserCreate(name="John", email="john@example.com", password="secret")
    created_user = await repo.create(user_data)

    assert created_user.id is not None
    assert created_user.name == "John"
    assert created_user.email == "john@example.com"

    user_by_id = await repo.get_by_id(created_user.id)
    assert user_by_id is not None
    assert user_by_id.id == created_user.id


@pytest.mark.asyncio
async def test_get_by_email(db_session):
    repo = UserRepository(db_session)

    email = "testuser@example.com"
    user_data = UserCreate(name="Test", email=email, password="123456")
    await repo.create(user_data)

    found_user = await repo.get_by_email(email)
    assert found_user is not None
    assert found_user.email == email


@pytest.mark.asyncio
async def test_update_name(db_session):
    repo = UserRepository(db_session)

    user_data = UserCreate(
        name="OldName", email="update_name@example.com", password="pass"
    )
    user = await repo.create(user_data)

    updated = await repo.update_name(user.id, "NewName")
    assert updated is True

    updated_user = await repo.get_by_id(user.id)
    assert updated_user.name == "NewName"
