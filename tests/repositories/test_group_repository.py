from uuid import uuid4

import pytest

from app.models import Group
from app.repositories.group_repository import GroupRepository


@pytest.mark.asyncio
async def test_create_and_get_by_id(db_session):
    repo = GroupRepository(db_session)

    group = Group(name="Test Group", owner_id=uuid4(), chat_id=uuid4())
    created = await repo.create(group)

    assert created.id is not None

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Test Group"


@pytest.mark.asyncio
async def test_add_and_is_member(db_session):
    repo = GroupRepository(db_session)

    group = await repo.create(Group(name="g1", owner_id=uuid4(), chat_id=uuid4()))
    user_id = uuid4()

    await repo.add_member(group.id, user_id)
    is_member = await repo.is_member(group.id, user_id)
    assert is_member is True


@pytest.mark.asyncio
async def test_remove_member(db_session):
    repo = GroupRepository(db_session)

    group = await repo.create(Group(name="g2", owner_id=uuid4(), chat_id=uuid4()))
    user_id = uuid4()

    await repo.add_member(group.id, user_id)
    await repo.remove_member(group.id, user_id)
    assert await repo.is_member(group.id, user_id) is False


@pytest.mark.asyncio
async def test_list_members_and_ids(db_session):
    repo = GroupRepository(db_session)

    group = await repo.create(Group(name="g3", owner_id=uuid4(), chat_id=uuid4()))
    user_ids = [uuid4() for _ in range(3)]
    for uid in user_ids:
        await repo.add_member(group.id, uid)

    member_ids = await repo.list_members_id(group.id)
    assert set(member_ids) == set(user_ids)


@pytest.mark.asyncio
async def test_list_user_groups(db_session):
    repo = GroupRepository(db_session)

    user_id = uuid4()
    for i in range(2):
        group = await repo.create(
            Group(name=f"Group {i}", owner_id=uuid4(), chat_id=uuid4())
        )
        await repo.add_member(group.id, user_id)

    groups = await repo.list_user_groups(user_id)
    assert len(groups) == 2


@pytest.mark.asyncio
async def test_get_by_chat_id(db_session):
    repo = GroupRepository(db_session)
    chat_id = uuid4()

    group = await repo.create(Group(name="g-chat", owner_id=uuid4(), chat_id=chat_id))
    result = await repo.get_by_chat_id(chat_id)

    assert result is not None
    assert result.chat_id == chat_id


@pytest.mark.asyncio
async def test_is_user_in_group_by_chat(db_session):
    repo = GroupRepository(db_session)

    chat_id = uuid4()
    user_id = uuid4()

    group = await repo.create(Group(name="g-check", owner_id=uuid4(), chat_id=chat_id))
    await repo.add_member(group.id, user_id)

    assert await repo.is_user_in_group_by_chat(chat_id, user_id) is True
    assert await repo.is_user_in_group_by_chat(chat_id, uuid4()) is False
