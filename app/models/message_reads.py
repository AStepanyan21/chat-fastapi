from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MessageRead(Base):
    __tablename__ = "message_reads"
    message_id: Mapped[UUID] = mapped_column(
        ForeignKey("messages.id"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
