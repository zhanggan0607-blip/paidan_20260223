"""add dingtalk fields to personnel

Revision ID: add_dingtalk_fields
Revises: add_photos_signature
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'add_dingtalk_fields'
down_revision: Union[str, None] = 'add_customer_signature'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('personnel')]
    
    if 'dingtalk_userid' not in columns:
        op.add_column('personnel', sa.Column('dingtalk_userid', sa.String(100), nullable=True, comment='钉钉用户ID'))
        op.create_index('idx_dingtalk_userid', 'personnel', ['dingtalk_userid'], unique=False)
    
    if 'dingtalk_unionid' not in columns:
        op.add_column('personnel', sa.Column('dingtalk_unionid', sa.String(100), nullable=True, comment='钉钉UnionID'))
    
    if 'dingtalk_avatar' not in columns:
        op.add_column('personnel', sa.Column('dingtalk_avatar', sa.String(500), nullable=True, comment='钉钉头像URL'))
    
    if 'dingtalk_title' not in columns:
        op.add_column('personnel', sa.Column('dingtalk_title', sa.String(100), nullable=True, comment='钉钉职位'))
    
    if 'is_synced' not in columns:
        op.add_column('personnel', sa.Column('is_synced', sa.Boolean, nullable=True, default=False, comment='是否从钉钉同步'))
        conn.execute(sa.text("UPDATE personnel SET is_synced = FALSE WHERE is_synced IS NULL"))


def downgrade() -> None:
    op.drop_index('idx_dingtalk_userid', table_name='personnel')
    op.drop_column('personnel', 'is_synced')
    op.drop_column('personnel', 'dingtalk_title')
    op.drop_column('personnel', 'dingtalk_avatar')
    op.drop_column('personnel', 'dingtalk_unionid')
    op.drop_column('personnel', 'dingtalk_userid')
