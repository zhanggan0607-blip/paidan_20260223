"""drop deprecated operation_type column from work_order_operation_log

Revision ID: drop_operation_type
Revises: remaining_jsonb
Create Date: 2026-05-02

"""
from alembic import op
import sqlalchemy as sa

revision = 'drop_operation_type'
down_revision = 'remaining_jsonb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('work_order_operation_log', 'operation_type',
                    existing_type=sa.String(50),
                    nullable=True,
                    server_default=None)


def downgrade() -> None:
    op.alter_column('work_order_operation_log', 'operation_type',
                    existing_type=sa.String(50),
                    nullable=False,
                    server_default='')
