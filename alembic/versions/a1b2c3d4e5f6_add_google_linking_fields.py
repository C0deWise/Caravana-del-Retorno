"""add google linking fields to usuario

Revision ID: a1b2c3d4e5f6
Revises: 0f4dd8a7b5d1
Create Date: 2026-07-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0f4dd8a7b5d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuario', sa.Column('us_google_id', sa.String(), nullable=True, unique=True))
    op.add_column('usuario', sa.Column('us_google_email', sa.String(), nullable=True))
    op.add_column('usuario', sa.Column('us_google_linked_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('usuario', 'us_google_linked_at')
    op.drop_column('usuario', 'us_google_email')
    op.drop_column('usuario', 'us_google_id')
