"""add composite indexes for spot_work

Revision ID: add_spot_work_indexes
Revises: add_work_content
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'add_spot_work_indexes'
down_revision: Union[str, None] = 'add_work_content'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_spot_status_created', 'spot_work', ['status', 'created_at'], unique=False)
    op.create_index('idx_spot_status_updated', 'spot_work', ['status', 'updated_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_spot_status_updated', table_name='spot_work')
    op.drop_index('idx_spot_status_created', table_name='spot_work')
