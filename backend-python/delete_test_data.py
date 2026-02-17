# -*- coding: utf-8 -*-
"""
删除所有测试数据脚本
删除带有 TESTDATA 标记的测试数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

TEST_SUFFIX = "TESTDATA"

def get_db_session():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def count_test_data(session):
    """统计测试数据数量"""
    counts = {}
    
    result = session.execute(text("""
        SELECT COUNT(*) as cnt FROM periodic_inspection 
        WHERE remarks LIKE :suffix OR inspection_id LIKE :suffix
    """), {"suffix": f"%{TEST_SUFFIX}%"})
    counts['periodic_inspection'] = result.scalar()
    
    result = session.execute(text("""
        SELECT COUNT(*) as cnt FROM temporary_repair 
        WHERE remarks LIKE :suffix OR repair_id LIKE :suffix
    """), {"suffix": f"%{TEST_SUFFIX}%"})
    counts['temporary_repair'] = result.scalar()
    
    result = session.execute(text("""
        SELECT COUNT(*) as cnt FROM spot_work 
        WHERE remarks LIKE :suffix OR work_id LIKE :suffix
    """), {"suffix": f"%{TEST_SUFFIX}%"})
    counts['spot_work'] = result.scalar()
    
    return counts

def delete_test_data(session):
    """删除测试数据"""
    results = {}
    
    periodic_count = session.execute(
        text("DELETE FROM periodic_inspection WHERE remarks LIKE :suffix OR inspection_id LIKE :suffix"),
        {"suffix": f"%{TEST_SUFFIX}%"}
    ).rowcount
    results['periodic_inspection'] = periodic_count
    
    repair_count = session.execute(
        text("DELETE FROM temporary_repair WHERE remarks LIKE :suffix OR repair_id LIKE :suffix"),
        {"suffix": f"%{TEST_SUFFIX}%"}
    ).rowcount
    results['temporary_repair'] = repair_count
    
    spot_work_count = session.execute(
        text("DELETE FROM spot_work WHERE remarks LIKE :suffix OR work_id LIKE :suffix"),
        {"suffix": f"%{TEST_SUFFIX}%"}
    ).rowcount
    results['spot_work'] = spot_work_count
    
    return results

def main():
    print("=" * 60)
    print("删除测试数据脚本")
    print(f"测试数据标识: {TEST_SUFFIX}")
    print("=" * 60)
    
    session, engine = get_db_session()
    
    try:
        counts = count_test_data(session)
        total = sum(counts.values())
        
        print("\n当前测试数据统计:")
        print(f"  定期巡检单: {counts['periodic_inspection']} 条")
        print(f"  临时维修单: {counts['temporary_repair']} 条")
        print(f"  零星用工单: {counts['spot_work']} 条")
        print(f"  总计: {total} 条")
        
        if total == 0:
            print("\n没有找到测试数据，无需删除。")
            return
        
        confirm = input("\n请确认是否要删除所有测试数据? (输入 'yes' 确认删除): ")
        
        if confirm.lower() != 'yes':
            print("\n取消删除操作。")
            return
        
        print("\n正在删除测试数据...")
        results = delete_test_data(session)
        session.commit()
        
        deleted_total = sum(results.values())
        
        print("\n" + "=" * 60)
        print("删除完成!")
        print(f"  定期巡检单: 删除 {results['periodic_inspection']} 条")
        print(f"  临时维修单: 删除 {results['temporary_repair']} 条")
        print(f"  零星用工单: 删除 {results['spot_work']} 条")
        print(f"  总计删除: {deleted_total} 条")
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
