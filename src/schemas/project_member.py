from pydantic import BaseModel, ConfigDict
from src.models.project_member import MemberRole, MemberStatus
from uuid import UUID


class InviteMemberRequest(BaseModel):
    username: str
    role: MemberRole = MemberRole.MEMBER


class MemberResponse(BaseModel):
    user_id: UUID
    project_id: UUID
    role: MemberRole
    status: MemberStatus

    model_config = ConfigDict(from_attributes=True)


class UpdateMemberRoleRequest(BaseModel):
    role: MemberRole
