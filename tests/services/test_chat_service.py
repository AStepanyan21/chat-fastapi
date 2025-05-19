from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.models import Chat, Group, Message, User
from app.models.chat import ChatType
from app.models.group import group_members
from app.repositories.message_repository import MessageRepository
from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    service = ChatService(db_session)
    chat = await service.repo.create(Chat(name="test", type=ChatType.private))
    result = await service.get_by_id(chat.id)
    assert result is not None
    assert result.id == chat.id


@pytest.mark.asyncio
async def test_list_all(db_session):
    service = ChatService(db_session)
    for i in range(3):
        await service.repo.create(Chat(name=f"chat-{i}", type=ChatType.public))
    chats = await service.list_all()
    assert len(chats) >= 3


@pytest.mark.asyncio
async def test_get_or_create_private_chat_create(db_session):
    service = ChatService(db_session)
    message_repo = MessageRepository(db_session)

    user1 = User(id=uuid4(), name="Alice", email="alice@test.com", password="123")
    user2 = User(id=uuid4(), name="Bob", email="bob@test.com", password="456")

    chat = await service.get_or_create_private_chat(user1, user2)

    await message_repo.create(
        Message(
            id=uuid4(),
            chat_id=chat.id,
            sender_id=user1.id,
            text="from user1",
            timestamp=datetime.now(),
        )
    )

    await message_repo.create(
        Message(
            id=uuid4(),
            chat_id=chat.id,
            sender_id=user2.id,
            text="from user2",
            timestamp=datetime.now(),
        )
    )

    chat2 = await service.get_or_create_private_chat(user1, user2)
    assert chat2.id == chat.id


@pytest.mark.asyncio
async def test_get_user_private_chats(db_session):
    service = ChatService(db_session)
    message_repo = MessageRepository(db_session)

    user = User(id=uuid4(), name="User", email="u@t.com", password="pass")
    chat = await service.repo.create(Chat(name="priv", type=ChatType.private))

    await message_repo.create(
        Message(
            id=uuid4(),
            chat_id=chat.id,
            sender_id=user.id,
            text="hello",
            timestamp=datetime.now(),
        )
    )

    chats = await service.get_user_private_chats(user.id)
    assert len(chats) == 1
    assert chats[0].id == chat.id


@pytest.mark.asyncio
async def test_get_all_user_chats(db_session):
    service = ChatService(db_session)
    message_repo = MessageRepository(db_session)

    user = User(id=uuid4(), name="Full", email="full@x.com", password="pw")

    priv = await service.repo.create(Chat(name="private", type=ChatType.private))

    await message_repo.create(
        Message(
            id=uuid4(),
            chat_id=priv.id,
            sender_id=user.id,
            text="from priv",
            timestamp=datetime.now() - timedelta(minutes=2),
        )
    )

    group_chat = await service.repo.create(Chat(name="group", type=ChatType.public))
    group = Group(name="grp", chat_id=group_chat.id, owner_id=uuid4())
    db_session.add(group)
    await db_session.flush()

    await db_session.execute(
        group_members.insert().values(group_id=group.id, user_id=user.id)
    )

    await message_repo.create(
        Message(
            id=uuid4(),
            chat_id=group_chat.id,
            sender_id=user.id,
            text="group msg",
            timestamp=datetime.now(),
        )
    )

    await db_session.commit()

    chats = await service.get_all_user_chats(user.id)
    assert len(chats) == 2
    assert chats[0].last_message_timestamp >= chats[1].last_message_timestamp


@pytest.mark.asyncio
async def test_has_access_to_chat(db_session):
    service = ChatService(db_session)
    message_repo = MessageRepository(db_session)

    user_id = uuid4()

    priv = await service.repo.create(Chat(name="p", type=ChatType.private))
    await message_repo.create(
        Message(
            id=uuid4(),
            chat_id=priv.id,
            sender_id=user_id,
            text="yo",
            timestamp=datetime.now(),
        )
    )

    group_chat = await service.repo.create(Chat(name="g", type=ChatType.public))
    group = Group(name="g2", chat_id=group_chat.id, owner_id=uuid4())
    db_session.add(group)
    await db_session.flush()

    await db_session.execute(
        group_members.insert().values(group_id=group.id, user_id=user_id)
    )
    await db_session.commit()

    assert await service.has_access_to_chat(priv, user_id) is True
    assert await service.has_access_to_chat(priv, uuid4()) is False
    assert await service.has_access_to_chat(group_chat, user_id) is True
    assert await service.has_access_to_chat(group_chat, uuid4()) is False
