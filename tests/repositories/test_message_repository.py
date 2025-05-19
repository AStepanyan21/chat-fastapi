from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.models import Group, Message
from app.repositories.message_repository import MessageRepository


@pytest.mark.asyncio
async def test_create_and_get_by_id(db_session):
    repo = MessageRepository(db_session)

    message = Message(
        chat_id=uuid4(), sender_id=uuid4(), text="Hello!", timestamp=datetime.now(UTC)
    )

    saved = await repo.create(message)
    fetched = await repo.get_by_id(saved.id)

    assert fetched is not None
    assert fetched.id == saved.id
    assert fetched.text == "Hello!"


@pytest.mark.asyncio
async def test_get_by_chat_id(db_session):
    repo = MessageRepository(db_session)
    chat_id = uuid4()

    for i in range(3):
        await repo.create(
            Message(
                chat_id=chat_id,
                sender_id=uuid4(),
                text=f"msg-{i}",
                timestamp=datetime.now(UTC),
            )
        )

    messages = await repo.get_by_chat_id(chat_id)
    assert len(messages) == 3
    assert all(m.chat_id == chat_id for m in messages)


@pytest.mark.asyncio
async def test_is_duplicate_message(db_session):
    repo = MessageRepository(db_session)
    chat_id = uuid4()
    sender_id = uuid4()
    timestamp = datetime.now(UTC)

    await repo.create(
        Message(
            chat_id=chat_id, sender_id=sender_id, text="duplicate", timestamp=timestamp
        )
    )

    assert (
        await repo.is_duplicate_message(chat_id, sender_id, "duplicate", timestamp)
        is True
    )
    assert (
        await repo.is_duplicate_message(chat_id, sender_id, "another", timestamp)
        is False
    )


@pytest.mark.asyncio
async def test_save_read_status_and_readers(db_session):
    repo = MessageRepository(db_session)

    message = Message(
        chat_id=uuid4(),
        sender_id=uuid4(),
        text="read test",
        timestamp=datetime.now(UTC),
    )
    await repo.create(message)

    user_id = uuid4()

    assert await repo.has_user_read(message.id, user_id) is False

    await repo.save_read_status(message.id, user_id)

    assert await repo.has_user_read(message.id, user_id) is True
    readers = await repo.get_readers(message.id)
    assert user_id in readers


@pytest.mark.asyncio
async def test_get_by_group_id(db_session):
    from app.models import Chat  # импорт внутри чтобы не падало без chat модели

    chat = Chat(id=uuid4(), name="test", type="public")
    db_session.add(chat)
    await db_session.flush()

    group = Group(name="group", owner_id=uuid4(), chat_id=chat.id)
    db_session.add(group)
    await db_session.flush()

    repo = MessageRepository(db_session)

    for i in range(2):
        await repo.create(
            Message(
                chat_id=chat.id,
                sender_id=uuid4(),
                text=f"msg {i}",
                timestamp=datetime.now(UTC),
            )
        )

    messages = await repo.get_by_group_id(group.id)
    assert len(messages) == 2
