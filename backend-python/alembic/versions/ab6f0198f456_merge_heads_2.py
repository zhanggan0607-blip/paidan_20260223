"""merge_heads_2

Revision ID: ab6f0198f456
Revises: add_created_by_temp_repair, add_maintenance_personnel_indexes
Create Date: 2026-05-13 12:53:28.775686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ab6f0198f456'
down_revision: Union[str, None] = ('add_created_by_temp_repair', 'add_maintenance_personnel_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
