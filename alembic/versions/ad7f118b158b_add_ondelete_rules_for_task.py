"""add ondelete rules for task

Revision ID: ad7f118b158b
Revises: 90bed45e746e
Create Date: 2026-02-27 10:09:47.727075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad7f118b158b'
down_revision: Union[str, Sequence[str], None] = '90bed45e746e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", recreate="always") as batch_op:
        batch_op.create_foreign_key(
            "fk_tasks_project_id_projects",
            "projects",
            ["project_id"],
            ["id"],
            ondelete="SET NULL",
        )

        batch_op.create_foreign_key(
            "fk_tasks_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", recreate="always") as batch_op:
        batch_op.create_foreign_key(
            "fk_tasks_project_id_projects",
            "projects",
            ["project_id"],
            ["id"],
        )

        batch_op.create_foreign_key(
            "fk_tasks_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
        )
