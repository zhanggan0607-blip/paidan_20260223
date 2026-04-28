from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE project_info ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE'))
    conn.execute(text('ALTER TABLE project_info ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP'))
    conn.execute(text('ALTER TABLE project_info ADD COLUMN IF NOT EXISTS deleted_by BIGINT'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_project_info_is_deleted ON project_info(is_deleted)'))
    conn.commit()
    print('Migration completed successfully')
