"""add work_content to spot_work

Revision ID: add_work_content
Revises: 
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'add_work_content'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('spot_work', sa.Column('work_content', sa.Text, nullable=True, comment='工作内容'))


def downgrade() -> None:
    op.drop_column('spot_work', 'work_content')
