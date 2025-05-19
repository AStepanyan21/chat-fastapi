from uuid import uuid4

import pytest

from app.models import User
from app.services.group_service import GroupService


@pytest.mark.asyncio
async def test_create_group(db_session):
    service = GroupService(db_session)

    owner = User(id=uuid4(), name="Owner", email="owner@test.com", password="pw")
    group = await service.create_group("Test Group", owner)

    assert group.name == "Test Group"
    assert group.owner_id == owner.id
    assert group.chat_id is not None

    assert await service.repo.is_member(group.id, owner.id) is True


@pytest.mark.asyncio
async def test_add_and_list_members(db_session):
    service = GroupService(db_session)
    owner = User(id=uuid4(), name="Owner", email="o@x.com", password="pw")
    user = User(id=uuid4(), name="User", email="u@x.com", password="pw")

    group = await service.create_group("Group", owner)

    await service.add_member(group.id, user.id)

    ids = await service.list_members_id(group.id)
    assert owner.id in ids
    assert user.id in ids

    members = await service.list_members(group.id)
    assert any(u.user_id == user.id for u in members)


@pytest.mark.asyncio
async def test_add_member_duplicate(db_session):
    service = GroupService(db_session)
    user = User(id=uuid4(), name="Dup", email="d@d.com", password="pw")

    group = await service.create_group("Dup Group", user)

    await service.add_member(group.id, user.id)  # Should not fail


@pytest.mark.asyncio
async def test_remove_member_success(db_session):
    service = GroupService(db_session)
    owner = User(id=uuid4(), name="Owner", email="o@x.com", password="pw")
    user = User(id=uuid4(), name="User", email="u@x.com", password="pw")

    group = await service.create_group("ToRemove", owner)
    await service.add_member(group.id, user.id)
    await service.remove_member(group.id, user.id)

    ids = await service.list_members_id(group.id)
    assert user.id not in ids
    assert owner.id in ids


@pytest.mark.asyncio
async def test_remove_owner_raises(db_session):
    service = GroupService(db_session)
    owner = User(id=uuid4(), name="Owner", email="o@x.com", password="pw")

    group = await service.create_group("FailRemoveOwner", owner)

    with pytest.raises(ValueError, match="Owner cannot be removed from group"):
        await service.remove_member(group.id, owner.id)


@pytest.mark.asyncio
async def test_list_user_groups(db_session):
    service = GroupService(db_session)
    user = User(id=uuid4(), name="U", email="e@e.com", password="pw")

    group1 = await service.create_group("G1", user)
    group2 = await service.create_group("G2", user)

    groups = await service.list_user_groups(user.id)
    assert len(groups) >= 2
    ids = [g.id for g in groups]
    assert group1.id in ids
    assert group2.id in ids


@pytest.mark.asyncio
async def test_get_by_id_and_chat_id(db_session):
    service = GroupService(db_session)
    owner = User(id=uuid4(), name="U", email="e@e.com", password="pw")

    group = await service.create_group("Check", owner)

    fetched = await service.get_by_id(group.id)
    assert fetched.id == group.id

    fetched2 = await service.get_by_chat_id(group.chat_id)
    assert fetched2.id == group.id
