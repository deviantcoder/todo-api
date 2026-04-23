from uuid import UUID

from fastapi import APIRouter, status

from src.api.deps.auth import CurrentUserDep
from src.api.deps.membership import MemberServiceDep
from src.models.membership import ProjectMember
from src.schemas.membership import (
    InviteMemberRequest,
    MemberResponse,
    UpdateMemberRoleRequest,
)

router = APIRouter(prefix='/projects/{project_id}/members', tags=['project members'])


@router.get('/', response_model=list[MemberResponse])
async def get_members(
    project_id: UUID,
    service: MemberServiceDep,
    current_user: CurrentUserDep
) -> list[ProjectMember]:
    return await service.get_members(project_id, current_user)


@router.post('/invite', response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    project_id: UUID,
    service: MemberServiceDep,
    current_user: CurrentUserDep,
    data: InviteMemberRequest
) -> ProjectMember:
    return await service.invite(project_id, data, current_user)


@router.post('/accept-invite', response_model=MemberResponse)
async def accept_invite(
    project_id: UUID,
    service: MemberServiceDep,
    current_user: CurrentUserDep
) -> ProjectMember:
    return await service.accept_invite(project_id, current_user)


@router.patch('/{user_id}/update-role', response_model=MemberResponse)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    service: MemberServiceDep,
    data: UpdateMemberRoleRequest,
    current_user: CurrentUserDep
) -> ProjectMember:
    return await service.update_role(
        project_id, user_id, data.role, current_user
    )


@router.delete('/leave', status_code=status.HTTP_204_NO_CONTENT)
async def leave_project(
    project_id: UUID,
    service: MemberServiceDep,
    current_user: CurrentUserDep
) -> None:
    return await service.leave(project_id, current_user)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    service: MemberServiceDep,
    current_user: CurrentUserDep
) -> None:
    return await service.remove_member(project_id, user_id, current_user)
