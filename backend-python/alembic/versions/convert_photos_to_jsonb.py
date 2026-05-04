"""convert photos columns from Text to JSONB

Revision ID: photos_jsonb
Revises:
Create Date: 2026-05-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'photos_jsonb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE spot_work
        ALTER COLUMN photos TYPE JSONB
        USING photos::jsonb;

        ALTER TABLE temporary_repair
        ALTER COLUMN photos TYPE JSONB
        USING photos::jsonb;

        ALTER TABLE periodic_inspection_record
        ALTER COLUMN photos TYPE JSONB
        USING photos::jsonb;
    """)

    op.execute("""
        UPDATE spot_work SET photos = '[]'::jsonb WHERE photos IS NULL;
        UPDATE temporary_repair SET photos = '[]'::jsonb WHERE photos IS NULL;
        UPDATE periodic_inspection_record SET photos = '[]'::jsonb WHERE photos IS NULL;
    """)

    op.execute("""
        ALTER TABLE spot_work ALTER COLUMN photos SET DEFAULT '[]'::jsonb;
        ALTER TABLE temporary_repair ALTER COLUMN photos SET DEFAULT '[]'::jsonb;
        ALTER TABLE periodic_inspection_record ALTER COLUMN photos SET DEFAULT '[]'::jsonb;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE spot_work ALTER COLUMN photos DROP DEFAULT;
        ALTER TABLE temporary_repair ALTER COLUMN photos DROP DEFAULT;
        ALTER TABLE periodic_inspection_record ALTER COLUMN photos DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE spot_work
        ALTER COLUMN photos TYPE Text
        USING photos::text;

        ALTER TABLE temporary_repair
        ALTER COLUMN photos TYPE Text
        USING photos::text;

        ALTER TABLE periodic_inspection_record
        ALTER COLUMN photos TYPE Text
        USING photos::text;
    """)
