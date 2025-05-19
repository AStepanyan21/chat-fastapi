from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ws.managers.chat_manager import ChatManager


@pytest.fixture
def manager():
    ChatManager._instances.clear()
    return ChatManager()


@pytest.fixture
def mock_websocket():
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect(manager, mock_websocket):
    await manager.connect("chat1", "user1", mock_websocket)

    assert "chat1" in manager.active_connections
    assert "user1" in manager.active_connections["chat1"]
    mock_websocket.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_removes_user(manager, mock_websocket):
    await manager.connect("chat1", "user1", mock_websocket)
    manager.disconnect("chat1", "user1")

    assert "chat1" not in manager.active_connections


@pytest.mark.asyncio
async def test_send_to_chat(manager, mock_websocket):
    await manager.connect("chat1", "user1", mock_websocket)
    await manager.connect("chat1", "user2", mock_websocket)

    msg = {"type": "test", "data": "hello"}
    await manager.send_to_chat("chat1", msg)

    assert mock_websocket.send_json.await_count == 2


@pytest.mark.asyncio
async def test_send_to_others(manager, mock_websocket):
    await manager.connect("chat1", "user1", mock_websocket)
    await manager.connect("chat1", "user2", mock_websocket)

    msg = {"type": "test", "data": "secret"}
    await manager.send_to_others("chat1", "user1", msg)

    assert mock_websocket.send_json.await_count == 1
