from uuid import UUID


def user_key_by_id(id: UUID) -> str:
    return f'user:id:{id}'


def user_key_by_username(username: str) -> str:
    return f'user:username:{username}'
