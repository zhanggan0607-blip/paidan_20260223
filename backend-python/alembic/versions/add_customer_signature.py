"""add customer_signature to temporary_repair

Revision ID: add_customer_signature
Revises: add_work_content_column
Create Date: 2025-01-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_customer_signature'
down_revision = 'add_work_content_column'
branch_labels = None
depends_on = None


def upgrade():
    # 添加客户签字字段到临时维修单表
    op.add_column('temporary_repair', sa.Column('customer_signature', sa.Text(), nullable=True, comment='客户签字Base64'))


def downgrade():
    op.drop_column('temporary_repair', 'customer_signature')
