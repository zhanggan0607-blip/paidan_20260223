"""merge heads

Revision ID: merge_heads
Revises: add_oss_storage_fields, drop_operation_type
Create Date: 2026-05-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'merge_heads'
down_revision = ('add_oss_storage_fields', 'drop_operation_type')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
