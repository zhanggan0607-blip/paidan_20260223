"""add oss storage fields

Revision ID: add_oss_storage_fields
Revises: create_uploaded_file
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_oss_storage_fields'
down_revision = 'create_uploaded_file'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'uploaded_file' AND column_name = 'storage_type'"
    ))
    if result.fetchone() is None:
        op.add_column('uploaded_file', sa.Column('storage_type', sa.String(20), server_default='database', comment='存储类型: oss/database'))
        op.add_column('uploaded_file', sa.Column('oss_url', sa.String(1000), nullable=True, comment='OSS访问URL'))
        op.create_index('idx_uploaded_storage_type', 'uploaded_file', ['storage_type'])

        conn.execute(sa.text(
            "UPDATE uploaded_file SET storage_type = 'database' WHERE storage_type IS NULL"
        ))
        conn.commit()


def downgrade() -> None:
    op.drop_index('idx_uploaded_storage_type', table_name='uploaded_file')
    op.drop_column('uploaded_file', 'oss_url')
    op.drop_column('uploaded_file', 'storage_type')
