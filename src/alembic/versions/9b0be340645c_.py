"""empty message

Revision ID: 9b0be340645c
Revises: 431cd365cd47
Create Date: 2026-05-09 11:40:15.754285

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9b0be340645c'
down_revision: Union[str, Sequence[str], None] = '431cd365cd47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column('users', sa.Column('search_vector', TSVECTOR, nullable=True))
    op.create_index('idx_users_search_vector', 'users', ['search_vector'], postgresql_using='gin')

    op.execute(
        """
            CREATE OR REPLACE FUNCTION update_user_search_vector()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.search_vector :=
                    setweight(to_tsvector('english', coalesce(NEW.username, '')), 'A') ||
                    setweight(to_tsvector('english', coalesce(NEW.email, '')), 'B') ||
                    setweight(to_tsvector('english', coalesce(NEW.full_name, '')), 'C');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
            CREATE TRIGGER users_search_vector_update
            BEFORE INSERT OR UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_user_search_vector();
        """
    )
    op.execute(
        """
            UPDATE users SET search_vector =
                setweight(to_tsvector('english', coalesce(username, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(email, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(full_name, '')), 'C')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute('DROP TRIGGER IF EXISTS users_search_vector_update ON users')
    op.execute('DROP FUNCTION IF EXISTS update_user_search_vector()')
    op.drop_index('idx_users_search_vector', table_name='users')
    op.drop_column('users', 'search_vector')
