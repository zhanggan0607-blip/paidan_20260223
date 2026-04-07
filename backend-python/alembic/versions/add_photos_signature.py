"""add photos and signature to spot_work

Revision ID: add_photos_signature
Revises: add_spot_work_indexes
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'add_photos_signature'
down_revision: Union[str, None] = 'add_spot_work_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('spot_work')]
    
    if 'photos' not in columns:
        op.add_column('spot_work', sa.Column('photos', sa.Text, nullable=True, comment='现场图片JSON数组'))
    if 'signature' not in columns:
        op.add_column('spot_work', sa.Column('signature', sa.Text, nullable=True, comment='班组签字图片'))


def downgrade() -> None:
    op.drop_column('spot_work', 'signature')
    op.drop_column('spot_work', 'photos')
