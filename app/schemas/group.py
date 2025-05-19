from typing import List
from uuid import UUID

from pydantic import BaseModel


class GroupCreateDTO(BaseModel):
    name: str
    member_ids: List[UUID]


class GroupUpdateMembersDTO(BaseModel):
    user_ids: List[UUID]


class GroupInfoDTO(BaseModel):
    id: UUID
    name: str
    owner: str
    inviter: str
    chat_id: UUID
