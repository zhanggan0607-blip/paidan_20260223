"""add client_contact_id to project_info

Revision ID: add_client_contact_id
Revises: add_customer_signature
Create Date: 2026-03-09

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_client_contact_id'
down_revision = 'add_dingtalk_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project_info', sa.Column('client_contact_id', sa.Integer(), nullable=True, comment='客户联系人ID'))
    
    op.create_foreign_key(
        'fk_project_info_client_contact_id',
        'project_info',
        'customer_contact',
        ['client_contact_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    op.create_index('idx_project_info_client_contact_id', 'project_info', ['client_contact_id'])


def downgrade():
    op.drop_index('idx_project_info_client_contact_id', table_name='project_info')
    op.drop_constraint('fk_project_info_client_contact_id', 'project_info', type_='foreignkey')
    op.drop_column('project_info', 'client_contact_id')
