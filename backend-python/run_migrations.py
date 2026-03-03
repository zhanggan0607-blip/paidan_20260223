"""
数据库迁移执行脚本
执行migrations目录下的SQL迁移文件
"""
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, SessionLocal


MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_executed_migrations(conn):
    """获取已执行的迁移记录"""
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'migration_history'
        )
    """))
    table_exists = result.scalar()
    
    if not table_exists:
        conn.execute(text("""
            CREATE TABLE migration_history (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL UNIQUE,
                executed_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
        return set()
    
    result = conn.execute(text("SELECT filename FROM migration_history"))
    return {row[0] for row in result.fetchall()}


def run_migration(filename: str):
    """执行单个迁移文件"""
    filepath = MIGRATIONS_DIR / filename
    
    if not filepath.exists():
        print(f"  ⚠️  文件不存在: {filename}")
        return False
    
    print(f"  📄 执行: {filename}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    session = SessionLocal()
    try:
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for stmt in statements:
            if stmt and not stmt.startswith('--'):
                session.execute(text(stmt))
        
        session.commit()
        print(f"  ✅ 成功: {filename}")
        
        session = SessionLocal()
        try:
            session.execute(text(
                "INSERT INTO migration_history (filename) VALUES (:filename)"
            ), {"filename": filename})
            session.commit()
        finally:
            session.close()
        return True
        
    except Exception as e:
        print(f"  ❌ 失败: {filename}")
        print(f"     错误: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()


def main():
    """主函数"""
    print("=" * 50)
    print("数据库迁移执行工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    migration_files = sorted([
        f for f in os.listdir(MIGRATIONS_DIR) 
        if f.endswith('.sql')
    ])
    
    if not migration_files:
        print("没有找到迁移文件")
        return
    
    print(f"\n发现 {len(migration_files)} 个迁移文件")
    
    try:
        with engine.connect() as conn:
            executed = get_executed_migrations(conn)
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {str(e)}")
        print("请检查后端服务是否正常运行，或直接通过API执行迁移")
        return
    
    pending = [f for f in migration_files if f not in executed]
    
    if not pending:
        print("\n✅ 所有迁移已执行，无需操作")
        return
    
    print(f"\n待执行迁移: {len(pending)} 个")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for filename in pending:
        if run_migration(filename):
            success_count += 1
        else:
            fail_count += 1
    
    print("-" * 50)
    print(f"\n执行完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    
    if fail_count == 0:
        print("✅ 所有迁移执行成功!")
    else:
        print("⚠️  部分迁移执行失败，请检查错误信息")


if __name__ == "__main__":
    main()
