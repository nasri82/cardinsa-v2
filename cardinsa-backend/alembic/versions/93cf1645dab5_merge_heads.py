"""merge_heads

Revision ID: 93cf1645dab5
Revises: 20251031_crating, 3484c1e61bef
Create Date: 2025-11-03 09:57:15.162811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93cf1645dab5'
down_revision: Union[str, None] = ('20251031_crating', '3484c1e61bef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
