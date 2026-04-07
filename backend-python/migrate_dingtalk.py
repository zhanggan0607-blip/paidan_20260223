"""
钉钉字段迁移脚本
直接执行SQL添加钉钉相关字段到personnel表
"""
from app.database import engine
from sqlalchemy import text


def migrate():
    with engine.connect() as conn:
        # 检查并添加钉钉相关字段
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'personnel'
        """))
        columns = [row[0] for row in result.fetchall()]
        
        if 'dingtalk_userid' not in columns:
            conn.execute(text('ALTER TABLE personnel ADD COLUMN dingtalk_userid VARCHAR(100) NULL'))
            print('Added dingtalk_userid column')
        
        if 'dingtalk_unionid' not in columns:
            conn.execute(text('ALTER TABLE personnel ADD COLUMN dingtalk_unionid VARCHAR(100) NULL'))
            print('Added dingtalk_unionid column')
        
        if 'dingtalk_avatar' not in columns:
            conn.execute(text('ALTER TABLE personnel ADD COLUMN dingtalk_avatar VARCHAR(500) NULL'))
            print('Added dingtalk_avatar column')
        
        if 'dingtalk_title' not in columns:
            conn.execute(text('ALTER TABLE personnel ADD COLUMN dingtalk_title VARCHAR(100) NULL'))
            print('Added dingtalk_title column')
        
        if 'is_synced' not in columns:
            conn.execute(text('ALTER TABLE personnel ADD COLUMN is_synced BOOLEAN DEFAULT FALSE'))
            print('Added is_synced column')
        
        # 创建索引
        try:
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_dingtalk_userid ON personnel(dingtalk_userid)'))
            print('Created idx_dingtalk_userid index')
        except Exception as e:
            print(f'Index creation skipped: {e}')
        
        conn.commit()
        print('Migration completed successfully!')


if __name__ == '__main__':
    migrate()
