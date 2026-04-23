from src.models.membership import ProjectMember, MemberStatus, MemberRole


def is_accepted(membership: ProjectMember) -> bool:
    return membership.status == MemberStatus.ACCEPTED


def _has_role(membership: ProjectMember, *roles: MemberRole) -> bool:
    return is_accepted(membership) and membership.role in roles


def can_manage_members(membership: ProjectMember) -> bool:
    return _has_role(membership, MemberRole.OWNER)


def can_edit_tasks(membership: ProjectMember) -> bool:
    return _has_role(membership, MemberRole.OWNER, MemberRole.MEMBER)


def can_view_tasks(membership: ProjectMember) -> bool:
    return is_accepted(membership)


def can_view_project(membership: ProjectMember) -> bool:
    return is_accepted(membership)
