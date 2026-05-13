"""add maintenance_personnel indexes

Revision ID: add_maintenance_personnel_indexes
Revises: add_photos_signature
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'add_maintenance_personnel_indexes'
down_revision: Union[str, None] = 'merge_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_temp_maintenance_personnel', 'temporary_repair', ['maintenance_personnel'], unique=False)
    op.create_index('idx_spot_maintenance_personnel', 'spot_work', ['maintenance_personnel'], unique=False)
    op.create_index('idx_insp_maintenance_personnel', 'periodic_inspection', ['maintenance_personnel'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_insp_maintenance_personnel', table_name='periodic_inspection')
    op.drop_index('idx_spot_maintenance_personnel', table_name='spot_work')
    op.drop_index('idx_temp_maintenance_personnel', table_name='temporary_repair')
