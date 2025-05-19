from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models import Chat, Group, Message, User
from app.models.chat import ChatType
from app.repositories.chat_repository import ChatRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.message_repository import MessageRepository
from app.services.group_service import GroupService
from app.services.message_service import MessageService
from app.services.socket_event_service import SocketEventService
from app.ws.enums import WebSocketEventType


class FakeSocketService(SocketEventService):
    def __init__(self):
        self.sent = []

    async def send_notification(self, user_id, event):
        self.sent.append((user_id, event))


@pytest.mark.asyncio
async def test_create_message_success(db_session):
    service = MessageService(
        db_session,
        group_service=GroupService(db_session),
        socket_service=FakeSocketService(),
    )

    msg = Message(
        chat_id=uuid4(), sender_id=uuid4(), text="Hello", timestamp=datetime.now()
    )

    result = await service.create_message(msg)
    assert result.id is not None
    assert result.text == "Hello"


@pytest.mark.asyncio
async def test_create_message_duplicate(db_session):
    service = MessageService(
        db_session,
        group_service=GroupService(db_session),
        socket_service=FakeSocketService(),
    )

    msg = Message(
        chat_id=uuid4(), sender_id=uuid4(), text="Duplicate", timestamp=datetime.now()
    )

    await service.repo.create(msg)

    with pytest.raises(HTTPException) as e:
        await service.create_message(msg)
    assert e.value.status_code == 429


@pytest.mark.asyncio
async def test_get_chat_messages(db_session):
    service = MessageService(
        db_session,
        group_service=GroupService(db_session),
        socket_service=FakeSocketService(),
    )

    user = User(id=uuid4(), name="Sender", email="s@t.com", password="pw")
    chat_id = uuid4()

    db_session.add(user)
    await db_session.flush()

    msg = Message(
        chat_id=chat_id, sender_id=user.id, text="msg", timestamp=datetime.now()
    )
    await service.repo.create(msg)

    result = await service.get_chat_messages(chat_id)
    assert any(m.text == "msg" for m in result)


@pytest.mark.asyncio
async def test_get_group_messages(db_session):
    chat_repo = ChatRepository(db_session)
    group_repo = GroupRepository(db_session)
    chat = await chat_repo.create(Chat(name="grp", type=ChatType.public))
    group = await group_repo.create(Group(name="g", chat_id=chat.id, owner_id=uuid4()))

    msg_repo = MessageRepository(db_session)
    await msg_repo.create(
        Message(
            chat_id=chat.id, sender_id=uuid4(), text="group", timestamp=datetime.now()
        )
    )

    service = MessageService(
        db_session,
        group_service=GroupService(db_session),
        socket_service=FakeSocketService(),
    )

    messages = await service.get_group_messages(group.id)
    assert any(m.text == "group" for m in messages)


@pytest.mark.asyncio
async def test_mark_as_read_not_group(db_session):
    socket_service = FakeSocketService()
    service = MessageService(
        db_session,
        group_service=GroupService(db_session),
        socket_service=socket_service,
    )

    msg = await service.repo.create(
        Message(
            chat_id=uuid4(),
            sender_id=uuid4(),
            text="readable",
            timestamp=datetime.now(),
        )
    )

    await service.mark_as_read(msg.id, uuid4())

    assert socket_service.sent
    assert socket_service.sent[0][1].type == WebSocketEventType.MESSAGE_READ


@pytest.mark.asyncio
async def test_mark_as_read_by_all(db_session):
    socket_service = FakeSocketService()
    group_service = GroupService(db_session)
    chat_repo = ChatRepository(db_session)
    group_repo = GroupRepository(db_session)
    message_repo = MessageRepository(db_session)

    chat = await chat_repo.create(Chat(name="chat", type=ChatType.public))
    group = await group_repo.create(Group(name="g", chat_id=chat.id, owner_id=uuid4()))

    user_ids = [uuid4(), uuid4(), uuid4()]
    for uid in user_ids:
        await group_repo.add_member(group.id, uid)

    msg = await message_repo.create(
        Message(
            chat_id=chat.id,
            sender_id=user_ids[0],
            text="readable",
            timestamp=datetime.now(),
        )
    )

    service = MessageService(
        db_session, group_service=group_service, socket_service=socket_service
    )

    for uid in user_ids[1:]:
        await message_repo.save_read_status(msg.id, uid)

    await service.mark_as_read(msg.id, user_ids[0])

    members = await group_service.list_members_id(group.id)
    readers = await message_repo.get_readers(msg.id)

    assert set(members).issubset(set(readers))
    assert socket_service.sent
    assert socket_service.sent[-1][1].type == WebSocketEventType.MESSAGE_READ_BY_ALL
