import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from datetime import datetime

def test_direct_insert():
    """直接在数据库中执行INSERT语句测试"""
    
    print("\n" + "="*80)
    print("🔍 直接INSERT测试")
    print("="*80 + "\n")
    
    settings = get_settings()
    print(f"📊 [数据库URL] {settings.database_url}\n")
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    try:
        # 测试1：检查表是否存在
        print("🔄 [测试1] 检查project_info表是否存在...")
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'project_info'
        """))
        table_exists = result.fetchone()
        
        if table_exists:
            print("✅ [测试1] project_info表存在\n")
        else:
            print("❌ [测试1] project_info表不存在！\n")
            return
        
        # 测试2：检查当前记录数
        print("🔄 [测试2] 检查当前记录数...")
        result = session.execute(text("SELECT COUNT(*) FROM project_info"))
        count_before = result.fetchone()[0]
        print(f"📊 [测试2] 当前记录数: {count_before}\n")
        
        # 测试3：执行INSERT语句
        print("🔄 [测试3] 执行INSERT语句...")
        test_project_id = f"DIRECT_TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        insert_sql = text("""
            INSERT INTO project_info (
                project_id, project_name, completion_date, maintenance_end_date,
                maintenance_period, client_name, address, project_abbr,
                client_contact, client_contact_position, client_contact_info
            ) VALUES (
                :project_id, :project_name, :completion_date, :maintenance_end_date,
                :maintenance_period, :client_name, :address, :project_abbr,
                :client_contact, :client_contact_position, :client_contact_info
            )
        """)
        
        insert_params = {
            'project_id': test_project_id,
            'project_name': '直接插入测试项目',
            'completion_date': datetime.now(),
            'maintenance_end_date': datetime.now(),
            'maintenance_period': '每月',
            'client_name': '直接插入测试客户',
            'address': '直接插入测试地址',
            'project_abbr': 'DIRECT',
            'client_contact': '直接插入测试联系人',
            'client_contact_position': '经理',
            'client_contact_info': '13900139000'
        }
        
        print(f"📤 [测试3] INSERT语句:")
        print(f"   project_id: {insert_params['project_id']}")
        print(f"   project_name: {insert_params['project_name']}")
        print(f"   completion_date: {insert_params['completion_date']}")
        print(f"   maintenance_end_date: {insert_params['maintenance_end_date']}")
        print(f"   maintenance_period: {insert_params['maintenance_period']}")
        print(f"   client_name: {insert_params['client_name']}")
        print(f"   address: {insert_params['address']}")
        print()
        
        result = session.execute(insert_sql, insert_params)
        session.commit()
        print(f"✅ [测试3] INSERT成功，影响行数: {result.rowcount}\n")
        
        # 测试4：验证插入的数据
        print("🔄 [测试4] 验证插入的数据...")
        result = session.execute(
            text("SELECT * FROM project_info WHERE project_id = :project_id"),
            {'project_id': test_project_id}
        )
        inserted_record = result.fetchone()
        
        if inserted_record:
            print("✅ [测试4] 数据已成功插入到数据库")
            print(f"   ID: {inserted_record[0]}")
            print(f"   project_id: {inserted_record[1]}")
            print(f"   project_name: {inserted_record[2]}")
            print(f"   created_at: {inserted_record[12]}")
            print()
        else:
            print("❌ [测试4] 数据未在数据库中找到！\n")
            return
        
        # 测试5：检查插入后的记录数
        print("🔄 [测试5] 检查插入后的记录数...")
        result = session.execute(text("SELECT COUNT(*) FROM project_info"))
        count_after = result.fetchone()[0]
        print(f"📊 [测试5] 插入后记录数: {count_after}")
        print(f"📊 [测试5] 新增记录数: {count_after - count_before}\n")
        
        # 测试6：清理测试数据
        print("🔄 [测试6] 清理测试数据...")
        result = session.execute(
            text("DELETE FROM project_info WHERE project_id = :project_id"),
            {'project_id': test_project_id}
        )
        session.commit()
        print(f"✅ [测试6] 清理完成，删除行数: {result.rowcount}\n")
        
        # 测试7：验证清理结果
        print("🔄 [测试7] 验证清理结果...")
        result = session.execute(
            text("SELECT COUNT(*) FROM project_info WHERE project_id = :project_id"),
            {'project_id': test_project_id}
        )
        remaining_count = result.fetchone()[0]
        
        if remaining_count == 0:
            print("✅ [测试7] 测试数据已完全清理\n")
        else:
            print(f"❌ [测试7] 仍有 {remaining_count} 条测试数据未清理\n")
        
        # 测试8：检查最终记录数
        print("🔄 [测试8] 检查最终记录数...")
        result = session.execute(text("SELECT COUNT(*) FROM project_info"))
        final_count = result.fetchone()[0]
        print(f"📊 [测试8] 最终记录数: {final_count}\n")
        
        print("="*80)
        print("✅ 所有测试完成！")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ [错误] {str(e)}\n")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    test_direct_insert()