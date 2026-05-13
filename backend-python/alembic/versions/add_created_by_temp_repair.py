"""add created_by to temporary_repair

Revision ID: add_created_by_temp_repair
Revises: add_customer_signature
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_created_by_temp_repair'
down_revision = 'add_customer_signature'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('temporary_repair', sa.Column('created_by', sa.String(100), nullable=True, comment='创建人'))
    op.create_index('idx_temp_created_by', 'temporary_repair', ['created_by'])


def downgrade() -> None:
    op.drop_index('idx_temp_created_by', table_name='temporary_repair')
    op.drop_column('temporary_repair', 'created_by')
