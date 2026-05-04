"""convert remaining Text JSON columns to JSONB

Revision ID: remaining_jsonb
Revises: photos_jsonb
Create Date: 2026-05-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'remaining_jsonb'
down_revision = 'photos_jsonb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE weekly_report
        ALTER COLUMN work_content TYPE JSONB
        USING work_content::jsonb;

        ALTER TABLE weekly_report
        ALTER COLUMN images TYPE JSONB
        USING images::jsonb;

        ALTER TABLE maintenance_log
        ALTER COLUMN images TYPE JSONB
        USING images::jsonb;

        ALTER TABLE maintenance_plan
        ALTER COLUMN inspection_items TYPE JSONB
        USING inspection_items::jsonb;
    """)

    op.execute("""
        UPDATE weekly_report SET work_content = '[]'::jsonb WHERE work_content IS NULL;
        UPDATE weekly_report SET images = '[]'::jsonb WHERE images IS NULL;
        UPDATE maintenance_log SET images = '[]'::jsonb WHERE images IS NULL;
        UPDATE maintenance_plan SET inspection_items = '[]'::jsonb WHERE inspection_items IS NULL;
    """)

    op.execute("""
        ALTER TABLE weekly_report ALTER COLUMN work_content SET DEFAULT '[]'::jsonb;
        ALTER TABLE weekly_report ALTER COLUMN images SET DEFAULT '[]'::jsonb;
        ALTER TABLE maintenance_log ALTER COLUMN images SET DEFAULT '[]'::jsonb;
        ALTER TABLE maintenance_plan ALTER COLUMN inspection_items SET DEFAULT '[]'::jsonb;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE weekly_report ALTER COLUMN work_content DROP DEFAULT;
        ALTER TABLE weekly_report ALTER COLUMN images DROP DEFAULT;
        ALTER TABLE maintenance_log ALTER COLUMN images DROP DEFAULT;
        ALTER TABLE maintenance_plan ALTER COLUMN inspection_items DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE weekly_report
        ALTER COLUMN work_content TYPE Text
        USING work_content::text;

        ALTER TABLE weekly_report
        ALTER COLUMN images TYPE Text
        USING images::text;

        ALTER TABLE maintenance_log
        ALTER COLUMN images TYPE Text
        USING images::text;

        ALTER TABLE maintenance_plan
        ALTER COLUMN inspection_items TYPE Text
        USING inspection_items::text;
    """)
