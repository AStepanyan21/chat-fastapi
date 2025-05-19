from app.ws.managers.chat_manager import ChatManager
from app.ws.managers.notification_manager import NotificationManager


def get_chat_manager() -> ChatManager:
    return ChatManager()


def get_notification_manager() -> NotificationManager:
    return NotificationManager()
