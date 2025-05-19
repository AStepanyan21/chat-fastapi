from datetime import datetime
from uuid import uuid4

import pytest

from app.models import Chat, Message
from app.models.chat import ChatType
from app.repositories.chat_repository import ChatRepository


@pytest.mark.asyncio
async def test_create_and_get_by_id(db_session):
    repo = ChatRepository(db_session)

    chat = Chat(name="Test Chat", type=ChatType.private)
    created = await repo.create(chat)

    assert created.id is not None
    assert created.name == "Test Chat"

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_list_all_chats(db_session):
    repo = ChatRepository(db_session)

    for i in range(3):
        await repo.create(Chat(name=f"Chat {i}", type=ChatType.public))

    all_chats = await repo.list_all()
    assert len(all_chats) >= 3


@pytest.mark.asyncio
async def test_get_by_ids(db_session):
    repo = ChatRepository(db_session)

    chat1 = await repo.create(Chat(name="c1", type=ChatType.private))
    chat2 = await repo.create(Chat(name="c2", type=ChatType.private))

    result = await repo.get_by_ids([chat1.id, chat2.id])
    assert {c.id for c in result} == {chat1.id, chat2.id}


@pytest.mark.asyncio
async def test_get_private_chat_between_users(db_session):
    repo = ChatRepository(db_session)

    chat = await repo.create(Chat(name="private", type=ChatType.private))
    user1, user2 = uuid4(), uuid4()

    db_session.add_all(
        [
            Message(
                chat_id=chat.id, sender_id=user1, text="hi", timestamp=datetime.now()
            ),
            Message(
                chat_id=chat.id, sender_id=user2, text="yo", timestamp=datetime.now()
            ),
        ]
    )
    await db_session.flush()

    result = await repo.get_private_chat_between_users(user1, user2)
    assert result is not None
    assert result.id == chat.id


@pytest.mark.asyncio
async def test_get_user_private_chats(db_session):
    repo = ChatRepository(db_session)

    user_id = uuid4()
    chat = await repo.create(Chat(name="pchat", type=ChatType.private))
    db_session.add(
        Message(
            chat_id=chat.id, sender_id=user_id, text="ping", timestamp=datetime.now()
        )
    )
    await db_session.flush()

    result = await repo.get_user_private_chats(user_id)
    assert len(result) == 1
    assert result[0].id == chat.id


@pytest.mark.asyncio
async def test_chat_to_dto(db_session):
    repo = ChatRepository(db_session)

    chat = await repo.create(Chat(name="dto", type=ChatType.private))
    now = datetime.now()

    db_session.add(
        Message(chat_id=chat.id, sender_id=uuid4(), text="last", timestamp=now)
    )
    await db_session.flush()

    dto = await repo.chat_to_dto(chat)
    assert dto.id == chat.id
    assert dto.last_message_timestamp == now


@pytest.mark.asyncio
async def test_is_user_in_private_chat(db_session):
    repo = ChatRepository(db_session)

    chat = await repo.create(Chat(name="check", type=ChatType.private))
    user_id = uuid4()

    db_session.add(
        Message(chat_id=chat.id, sender_id=user_id, text="yo", timestamp=datetime.now())
    )
    await db_session.flush()

    assert await repo.is_user_in_private_chat(chat.id, user_id) is True
    assert await repo.is_user_in_private_chat(chat.id, uuid4()) is False
