from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ws.managers.notification_manager import NotificationManager


@pytest.fixture
def manager():
    NotificationManager._instances.clear()
    return NotificationManager()


@pytest.fixture
def mock_websocket():
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect(manager, mock_websocket):
    await manager.connect("user123", mock_websocket)

    assert "user123" in manager.active_connections
    assert manager.active_connections["user123"] is mock_websocket
    mock_websocket.accept.assert_awaited_once()


def test_disconnect(manager, mock_websocket):
    manager.active_connections["user123"] = mock_websocket
    manager.disconnect("user123")

    assert "user123" not in manager.active_connections


@pytest.mark.asyncio
async def test_send_to_user(manager, mock_websocket):
    manager.active_connections["user123"] = mock_websocket

    msg = {"type": "notification", "data": "test"}
    await manager.send_to_user("user123", msg)

    mock_websocket.send_json.assert_awaited_once_with(msg)


@pytest.mark.asyncio
async def test_send_to_user_user_not_connected(manager):
    await manager.send_to_user("unknown_user", {"data": "noop"})
