"""merge con estado_curso

Revision ID: 7679d3c9cb6a
Revises: dc00e9041780, e1da8454900c
Create Date: 2026-05-09 12:47:26.853723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7679d3c9cb6a'
down_revision: Union[str, Sequence[str], None] = ('dc00e9041780', 'e1da8454900c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
