from typing import Dict

from fastapi import WebSocket

from app.ws.managers.base_singleton import SingletonMeta


class ChatManager(metaclass=SingletonMeta):
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, chat_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = {}
        self.active_connections[chat_id][user_id] = websocket

    def disconnect(self, chat_id: str, user_id: str):
        chat_conns = self.active_connections.get(chat_id)
        if chat_conns and user_id in chat_conns:
            chat_conns.pop(user_id, None)
            if not chat_conns:
                self.active_connections.pop(chat_id)

    async def send_to_chat(self, chat_id: str, message: dict):
        chat_conns = self.active_connections.get(chat_id, {})
        for ws in chat_conns.values():
            await ws.send_json(message)

    async def send_to_others(self, chat_id: str, sender_id: str, message: dict):
        chat_conns = self.active_connections.get(chat_id, {})
        for uid, ws in chat_conns.items():
            if uid != sender_id:
                await ws.send_json(message)
