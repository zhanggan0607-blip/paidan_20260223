"""create uploaded_file table

Revision ID: create_uploaded_file
Revises: add_customer_signature
Create Date: 2026-03-30

"""
from alembic import op
import sqlalchemy as sa


revision = 'create_uploaded_file'
down_revision = 'add_client_contact_id'
branch_labels = None
depends_on = None


def upgrade():
    """
    创建上传文件表
    用于将图片等文件存储在数据库中，确保数据永久保存在阿里云RDS
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'uploaded_file' not in inspector.get_table_names():
        op.create_table(
            'uploaded_file',
            sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
            sa.Column('file_id', sa.String(36), nullable=False, comment='文件唯一标识UUID'),
            sa.Column('original_filename', sa.String(255), nullable=True, comment='原始文件名'),
            sa.Column('stored_filename', sa.String(255), nullable=False, comment='存储文件名'),
            sa.Column('content_type', sa.String(100), nullable=True, comment='文件MIME类型'),
            sa.Column('file_data', sa.LargeBinary(), nullable=False, comment='文件二进制数据'),
            sa.Column('file_size', sa.BigInteger(), nullable=False, comment='文件大小(字节)'),
            sa.Column('file_path', sa.String(500), nullable=True, comment='文件路径(用于兼容旧数据)'),
            sa.Column('upload_date', sa.String(10), nullable=False, comment='上传日期(YYYYMMDD)'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('file_id'),
            comment='上传文件表'
        )
        
        op.create_index('idx_uploaded_file_id', 'uploaded_file', ['file_id'])
        op.create_index('idx_uploaded_file_path', 'uploaded_file', ['file_path'])
        op.create_index('idx_uploaded_upload_date', 'uploaded_file', ['upload_date'])


def downgrade():
    op.drop_index('idx_uploaded_upload_date', table_name='uploaded_file')
    op.drop_index('idx_uploaded_file_path', table_name='uploaded_file')
    op.drop_index('idx_uploaded_file_id', table_name='uploaded_file')
    op.drop_table('uploaded_file')
