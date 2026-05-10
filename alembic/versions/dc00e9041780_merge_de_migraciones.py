"""merge de migraciones

Revision ID: dc00e9041780
Revises: 6211ec8da47a, adebc859019a, cf14f7b3d9c2
Create Date: 2026-05-08 23:08:03.425462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc00e9041780'
down_revision: Union[str, Sequence[str], None] = ('6211ec8da47a', 'adebc859019a', 'cf14f7b3d9c2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
