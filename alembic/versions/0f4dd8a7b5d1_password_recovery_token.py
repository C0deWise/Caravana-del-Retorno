"""password recovery token

Revision ID: 0f4dd8a7b5d1
Revises: 68737714ecd4
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f4dd8a7b5d1'
down_revision: Union[str, Sequence[str], None] = '68737714ecd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'password_recovery_token',
        sa.Column('prt_codigo', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('us_codigo', sa.Integer(), nullable=False),
        sa.Column('prt_jti_hash', sa.String(length=64), nullable=False),
        sa.Column('prt_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('prt_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('prt_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prt_revocado', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['us_codigo'], ['usuario.us_codigo'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('prt_codigo'),
        sa.UniqueConstraint('prt_jti_hash', name='uq_password_recovery_token_jti_hash'),
    )


def downgrade() -> None:
    op.drop_table('password_recovery_token')