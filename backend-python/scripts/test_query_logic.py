import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

def test_query_logic():
    """测试数据库查询逻辑"""
    
    print("\n" + "="*80)
    print("🔍 数据库查询逻辑测试")
    print("="*80 + "\n")
    
    settings = get_settings()
    print(f"📊 [数据库URL] {settings.database_url}\n")
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    try:
        # 测试1：查询总数
        print("🔄 [测试1] 查询总数...")
        result = session.execute(text("SELECT COUNT(*) FROM project_info"))
        total_count = result.fetchone()[0]
        print(f"📊 [测试1] 总记录数: {total_count}\n")
        
        # 测试2：查询第一页（page=0, size=10）
        print("🔄 [测试2] 查询第一页（page=0, size=10）...")
        query = text("""
            SELECT * FROM project_info
            ORDER BY created_at DESC
            LIMIT 10 OFFSET 0
        """)
        result = session.execute(query)
        page1_items = result.fetchall()
        print(f"📊 [测试2] 第一页记录数: {len(page1_items)}\n")
        
        # 测试3：查询第二页（page=1, size=10）
        print("🔄 [测试3] 查询第二页（page=1, size=10）...")
        query = text("""
            SELECT * FROM project_info
            ORDER BY created_at DESC
            LIMIT 10 OFFSET 10
        """)
        result = session.execute(query)
        page2_items = result.fetchall()
        print(f"📊 [测试3] 第二页记录数: {len(page2_items)}\n")
        
        # 测试4：带项目名称筛选
        print("🔄 [测试4] 带项目名称筛选（project_name LIKE '%测试%'）...")
        query = text("""
            SELECT COUNT(*) FROM project_info
            WHERE project_name LIKE :project_name
        """)
        result = session.execute(query, {'project_name': '%测试%'})
        filtered_count = result.fetchone()[0]
        print(f"📊 [测试4] 筛选后记录数: {filtered_count}\n")
        
        # 测试5：带客户名称筛选
        print("🔄 [测试5] 带客户名称筛选（client_name LIKE '%北京%'）...")
        query = text("""
            SELECT COUNT(*) FROM project_info
            WHERE client_name LIKE :client_name
        """)
        result = session.execute(query, {'client_name': '%北京%'})
        filtered_count = result.fetchone()[0]
        print(f"📊 [测试5] 筛选后记录数: {filtered_count}\n")
        
        # 测试6：检查是否有重复记录
        print("🔄 [测试6] 检查是否有重复记录...")
        query = text("""
            SELECT project_id, COUNT(*) as cnt
            FROM project_info
            GROUP BY project_id
            HAVING COUNT(*) > 1
        """)
        result = session.execute(query)
        duplicates = result.fetchall()
        
        if duplicates:
            print(f"❌ [测试6] 发现 {len(duplicates)} 条重复记录:")
            for dup in duplicates:
                print(f"   - project_id={dup[0]}, count={dup[1]}")
        else:
            print(f"✅ [测试6] 没有重复记录\n")
        
        # 测试7：检查所有记录的ID是否唯一
        print("🔄 [测试7] 检查ID唯一性...")
        query = text("""
            SELECT id, COUNT(*) as cnt
            FROM project_info
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        result = session.execute(query)
        duplicates = result.fetchall()
        
        if duplicates:
            print(f"❌ [测试7] 发现 {len(duplicates)} 条重复ID:")
            for dup in duplicates:
                print(f"   - id={dup[0]}, count={dup[1]}")
        else:
            print(f"✅ [测试7] 所有ID都是唯一的\n")
        
        # 测试8：检查是否有NULL值
        print("🔄 [测试8] 检查必填字段是否有NULL值...")
        query = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN project_id IS NULL THEN 1 END) as null_project_id,
                COUNT(CASE WHEN project_name IS NULL THEN 1 END) as null_project_name,
                COUNT(CASE WHEN completion_date IS NULL THEN 1 END) as null_completion_date,
                COUNT(CASE WHEN maintenance_end_date IS NULL THEN 1 END) as null_maintenance_end_date,
                COUNT(CASE WHEN maintenance_period IS NULL THEN 1 END) as null_maintenance_period,
                COUNT(CASE WHEN client_name IS NULL THEN 1 END) as null_client_name,
                COUNT(CASE WHEN address IS NULL THEN 1 END) as null_address
            FROM project_info
        """)
        result = session.execute(query)
        null_check = result.fetchone()
        
        print(f"📊 [测试8] NULL值检查:")
        print(f"   - 总记录数: {null_check[0]}")
        print(f"   - NULL project_id: {null_check[1]}")
        print(f"   - NULL project_name: {null_check[2]}")
        print(f"   - NULL completion_date: {null_check[3]}")
        print(f"   - NULL maintenance_end_date: {null_check[4]}")
        print(f"   - NULL maintenance_period: {null_check[5]}")
        print(f"   - NULL client_name: {null_check[6]}")
        print(f"   - NULL address: {null_check[7]}\n")
        
        # 测试9：模拟前端查询（page=0, size=10, 无筛选）
        print("🔄 [测试9] 模拟前端查询（page=0, size=10, 无筛选）...")
        query = text("""
            SELECT 
                id, project_id, project_name, completion_date, 
                maintenance_end_date, maintenance_period, client_name, 
                address, project_abbr, client_contact, 
                client_contact_position, client_contact_info, 
                created_at, updated_at
            FROM project_info
            ORDER BY created_at DESC
            LIMIT 10 OFFSET 0
        """)
        result = session.execute(query)
        items = result.fetchall()
        
        print(f"📊 [测试9] 查询结果:")
        print(f"   - 记录数: {len(items)}")
        print(f"   - ID范围: {items[0][0]} 到 {items[-1][0] if items else 'N/A'}")
        print()
        
        print("="*80)
        print("✅ 查询逻辑测试完成！")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ [错误] {str(e)}\n")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    test_query_logic()