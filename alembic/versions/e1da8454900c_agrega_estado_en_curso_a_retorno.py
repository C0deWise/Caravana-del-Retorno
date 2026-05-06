"""Agrega estado 'EN_CURSO' a retorno

Revision ID: e1da8454900c
Revises: dc6ab2fc7af5
Create Date: 2026-05-06 15:25:38.496798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1da8454900c'
down_revision: Union[str, Sequence[str], None] = 'dc6ab2fc7af5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE retornoestado ADD VALUE 'EN_CURSO'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
