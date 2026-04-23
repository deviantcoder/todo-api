from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.membership import MemberRole, MemberStatus


class InviteMemberRequest(BaseModel):
    username: str
    role: MemberRole = MemberRole.MEMBER


class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID
    role: MemberRole
    status: MemberStatus

    model_config = ConfigDict(from_attributes=True)


class UpdateMemberRoleRequest(BaseModel):
    role: MemberRole
