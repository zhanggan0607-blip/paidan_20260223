"""
数据库迁移API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from pathlib import Path
import os

from app.database import SessionLocal
from app.auth import get_current_admin_user

router = APIRouter(prefix="/migration", tags=["迁移管理"])

MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


@router.get("/status")
def get_migration_status(current_user = Depends(get_current_admin_user)):
    """
    获取迁移状态
    """
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'migration_history'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            return {
                "initialized": False,
                "executed": [],
                "pending": sorted([
                    f for f in os.listdir(MIGRATIONS_DIR) 
                    if f.endswith('.sql')
                ])
            }
        
        result = session.execute(text("SELECT filename FROM migration_history"))
        executed = [row[0] for row in result.fetchall()]
        
        all_migrations = sorted([
            f for f in os.listdir(MIGRATIONS_DIR) 
            if f.endswith('.sql')
        ])
        pending = [f for f in all_migrations if f not in executed]
        
        return {
            "initialized": True,
            "executed": executed,
            "pending": pending
        }
    finally:
        session.close()


@router.post("/execute")
def execute_migrations(current_user = Depends(get_current_admin_user)):
    """
    执行所有待执行的迁移
    """
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'migration_history'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            session.execute(text("""
                CREATE TABLE migration_history (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL UNIQUE,
                    executed_at TIMESTAMP DEFAULT NOW()
                )
            """))
            session.commit()
            executed = set()
        else:
            result = session.execute(text("SELECT filename FROM migration_history"))
            executed = {row[0] for row in result.fetchall()}
        
        migration_files = sorted([
            f for f in os.listdir(MIGRATIONS_DIR) 
            if f.endswith('.sql')
        ])
        
        pending = [f for f in migration_files if f not in executed]
        
        if not pending:
            return {
                "success": True,
                "message": "所有迁移已执行，无需操作",
                "executed_count": 0
            }
        
        success_count = 0
        fail_count = 0
        errors = []
        
        for filename in pending:
            filepath = MIGRATIONS_DIR / filename
            
            if not filepath.exists():
                fail_count += 1
                errors.append(f"{filename}: 文件不存在")
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            try:
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for stmt in statements:
                    if stmt and not stmt.startswith('--'):
                        session.execute(text(stmt))
                
                session.execute(text(
                    "INSERT INTO migration_history (filename) VALUES (:filename)"
                ), {"filename": filename})
                session.commit()
                success_count += 1
                
            except Exception as e:
                session.rollback()
                fail_count += 1
                errors.append(f"{filename}: {str(e)}")
        
        return {
            "success": fail_count == 0,
            "message": f"执行完成: 成功 {success_count} 个, 失败 {fail_count} 个",
            "executed_count": success_count,
            "failed_count": fail_count,
            "errors": errors
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/execute/{filename}")
def execute_single_migration(filename: str, current_user = Depends(get_current_admin_user)):
    """
    执行单个迁移文件
    """
    filepath = MIGRATIONS_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"迁移文件不存在: {filename}")
    
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'migration_history'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            session.execute(text("""
                CREATE TABLE migration_history (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL UNIQUE,
                    executed_at TIMESTAMP DEFAULT NOW()
                )
            """))
            session.commit()
        else:
            result = session.execute(text(
                "SELECT 1 FROM migration_history WHERE filename = :filename"
            ), {"filename": filename})
            if result.fetchone():
                return {
                    "success": True,
                    "message": f"迁移 {filename} 已执行过"
                }
        
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for stmt in statements:
            if stmt and not stmt.startswith('--'):
                session.execute(text(stmt))
        
        session.execute(text(
            "INSERT INTO migration_history (filename) VALUES (:filename)"
        ), {"filename": filename})
        session.commit()
        
        return {
            "success": True,
            "message": f"迁移 {filename} 执行成功"
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
