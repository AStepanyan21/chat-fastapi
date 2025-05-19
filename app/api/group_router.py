from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_group_service, get_socket_event_service
from app.models import User
from app.schemas.base_event import WebSocketEvent
from app.schemas.group import GroupCreateDTO, GroupInfoDTO, GroupUpdateMembersDTO
from app.schemas.user import UserRead
from app.services.group_service import GroupService
from app.services.socket_event_service import SocketEventService
from app.ws.enums import WebSocketEventType

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("/", response_model=GroupInfoDTO)
async def create_group(
    dto: GroupCreateDTO,
    group_service: GroupService = Depends(get_group_service),
    socket_event_service: SocketEventService = Depends(get_socket_event_service),
    current_user: User = Depends(get_current_user),
):
    group = await group_service.create_group(dto.name, current_user)

    for member_id in dto.member_ids:
        if member_id != current_user.id:
            await group_service.add_member(group.id, member_id)

    member_ids = await group_service.list_members_id(group.id)

    event = WebSocketEvent[GroupInfoDTO](
        type=WebSocketEventType.GROUP_UPDATED,
        data=GroupInfoDTO(
            id=group.id,
            name=group.name,
            owner=current_user.name,
            inviter=current_user.name,
            chat_id=group.chat_id,
        ),
    )

    await socket_event_service.send_to_users(user_ids=member_ids, event=event)

    return event


@router.post("/{group_id}/members")
async def add_members(
    group_id: UUID,
    dto: GroupUpdateMembersDTO,
    group_service: GroupService = Depends(get_group_service),
    socket_event_service: SocketEventService = Depends(get_socket_event_service),
    current_user: User = Depends(get_current_user),
):
    group = await group_service.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    for user_id in dto.user_ids:
        await group_service.add_member(group_id, user_id)

    event = WebSocketEvent[GroupInfoDTO](
        type=WebSocketEventType.GROUP_UPDATED,
        data=GroupInfoDTO(
            id=group.id,
            name=group.name,
            owner=current_user.name,
            inviter=current_user.name,
            chat_id=group.chat_id,
        ),
    )

    await socket_event_service.send_to_users(user_ids=dto.user_ids, event=event)

    return {"detail": "Members added"}


@router.delete("/{group_id}/members")
async def remove_members(
    group_id: UUID,
    dto: GroupUpdateMembersDTO,
    group_service: GroupService = Depends(get_group_service),
    socket_event_service: SocketEventService = Depends(get_socket_event_service),
    current_user: User = Depends(get_current_user),
):
    group = await group_service.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    for user_id in dto.user_ids:
        await group_service.remove_member(group_id, user_id)

    remaining_members = await group_service.list_members_id(group_id)

    event = WebSocketEvent[GroupInfoDTO](
        type=WebSocketEventType.GROUP_UPDATED,
        data=GroupInfoDTO(
            id=group.id,
            name=group.name,
            owner=current_user.name,
            inviter=current_user.name,
            chat_id=group.chat_id,
        ),
    )

    await socket_event_service.send_to_users(user_ids=remaining_members, event=event)

    return {"detail": "Members removed"}


@router.get("/{group_id}/members", response_model=list[UserRead])
async def list_members(
    group_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    group_service: GroupService = Depends(get_group_service),
):
    group = await group_service.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return await group_service.list_members(group_id, offset, limit)
