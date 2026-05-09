"""merge num_parqueadero vehiculo y fecha, genero persona

Revision ID: eb3ab23bbef1
Revises: 6211ec8da47a, cf14f7b3d9c2
Create Date: 2026-05-08 09:33:06.898567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb3ab23bbef1'
down_revision: Union[str, Sequence[str], None] = ('6211ec8da47a', 'cf14f7b3d9c2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
