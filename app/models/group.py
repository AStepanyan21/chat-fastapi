import uuid

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id")),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
)


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="owned_groups")
    members = relationship("User", secondary=group_members, backref="groups_joined")
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
