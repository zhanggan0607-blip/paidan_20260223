import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import random

def insert_test_data():
    """插入测试数据到数据库"""
    
    # 数据库配置
    db_host = "localhost"
    db_port = 5432
    db_user = "postgres"
    db_name = "tq"
    db_password = "123456"
    
    print(f"正在连接到数据库 '{db_name}'...")
    
    try:
        # 连接到数据库
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ 连接成功！")
        print()
        
        # 清空现有数据（可选）
        print("🗑️  清空现有数据...")
        cursor.execute("TRUNCATE TABLE maintenance_plan CASCADE;")
        cursor.execute("TRUNCATE TABLE project_info CASCADE;")
        cursor.execute("TRUNCATE TABLE personnel CASCADE;")
        cursor.execute("TRUNCATE TABLE periodic_inspection CASCADE;")
        cursor.execute("TRUNCATE TABLE inspection_item CASCADE;")
        print("✅ 数据清空完成！")
        print()
        
        # 插入项目信息
        print("📝 正在插入项目信息...")
        projects = [
            ('PRJ-2025-001', '上海中心大厦维保项目', '2024-12-31', '2026-12-31', '每半年', 
             '上海城投（集团）有限公司', '上海市浦东新区陆家嘴银城中路501号', 'SSTCP', 
             '张经理', '项目经理', '13800138000'),
            ('PRJ-2025-002', '环球金融中心维保项目', '2023-06-30', '2025-06-30', '每半年', 
             '上海建工集团股份有限公司', '上海市浦东新区世纪大道100号', 'SWFC', 
             '李总监', '工程总监', '13900139000'),
            ('PRJ-2025-003', '金茂大厦维保项目', '2024-03-15', '2025-03-15', '每季度', 
             '中国金茂控股集团有限公司', '上海市浦东新区世纪大道88号', 'JM', 
             '王主管', '运维主管', '13700137000'),
            ('PRJ-2025-004', '东方明珠塔维保项目', '2024-09-01', '2025-03-01', '每月', 
             '上海文化广播影视集团有限公司', '上海市浦东新区世纪大道1号', 'OP', 
             '赵经理', '设备经理', '13600136000'),
            ('PRJ-2025-005', '上海博物馆维保项目', '2024-06-30', '2026-06-30', '每季度', 
             '上海博物馆', '上海市黄浦区人民大道201号', 'MUSEUM', 
             '孙主任', '设施主任', '13500135000'),
        ]
        
        for project in projects:
            cursor.execute("""
                INSERT INTO project_info (project_id, project_name, completion_date, maintenance_end_date, 
                                     maintenance_period, client_name, address, project_abbr, 
                                     client_contact, client_contact_position, client_contact_info)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, project)
        
        print(f"✅ 插入了 {len(projects)} 条项目信息")
        print()
        
        # 插入人员信息
        print("👥 正在插入人员信息...")
        personnel = [
            ('刘园智', '男', '13800138001', '维保部', '工程师', '上海市浦东新区张江高科技园区', '高级工程师'),
            ('晋海龙', '男', '13900139002', '维保部', '技术员', '上海市浦东新区金桥出口加工区', '技术专家'),
            ('张伟', '男', '13700137003', '维保部', '工程师', '上海市浦东新区外高桥保税区', '资深工程师'),
            ('李明', '男', '13600136004', '维保部', '技术员', '上海市浦东新区陆家嘴金融贸易区', '技术骨干'),
            ('王芳', '女', '13500135005', '行政部', '管理员', '上海市浦东新区张江高科技园区', '行政主管'),
            ('赵强', '男', '13400134006', '维保部', '工程师', '上海市浦东新区金桥出口加工区', '工程师'),
        ]
        
        for person in personnel:
            cursor.execute("""
                INSERT INTO personnel (name, gender, phone, department, role, address, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, person)
        
        print(f"✅ 插入了 {len(personnel)} 条人员信息")
        print()
        
        # 插入维保计划
        print("📋 正在插入维保计划...")
        base_date = datetime.now()
        maintenance_plans = []
        
        for i in range(10):
            plan_id = f'MP-2025-{str(i+1).zfill(3)}'
            project = projects[i % len(projects)]
            person = personnel[i % len(personnel)]
            
            plan_start_date = base_date + timedelta(days=i*7)
            plan_end_date = plan_start_date + timedelta(days=30)
            
            maintenance_plans.append((
                plan_id,
                f'{project[1]} - 第{i+1}期维保',
                project[0],
                random.choice(['定期维保', '预防性维保', '故障维修', '巡检']),
                f'EQ-{random.randint(1000, 9999)}',
                f'电梯系统-{i+1}',
                f'MODEL-{random.randint(100, 999)}',
                f'位置-{i+1}层',
                plan_start_date,
                plan_end_date,
                plan_start_date + timedelta(days=7) if i % 2 == 0 else None,
                plan_end_date + timedelta(days=30),
                person[0],
                '维保部',
                person[2],
                f'维保内容：检查电梯系统运行状态，更换磨损部件，测试安全装置',
                '按照国家标准GB7588-2003执行',
                '符合国家电梯安全规范',
                random.choice(['待执行', '执行中', '已完成', '已延期']),
                random.choice(['未开始', '进行中', '已完成', '已取消']),
                random.randint(0, 100),
                f'备注：这是第{i+1}期维保计划，需要特别注意安全事项'
            ))
        
        for plan in maintenance_plans:
            cursor.execute("""
                INSERT INTO maintenance_plan (plan_id, plan_name, project_id, plan_type, equipment_id, equipment_name,
                                            equipment_model, equipment_location, plan_start_date, plan_end_date,
                                            execution_date, next_maintenance_date, responsible_person,
                                            responsible_department, contact_info, maintenance_content,
                                            maintenance_requirements, maintenance_standard, plan_status,
                                            execution_status, completion_rate, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, plan)
        
        print(f"✅ 插入了 {len(maintenance_plans)} 条维保计划")
        print()
        
        # 插入定期巡检
        print("🔍 正在插入定期巡检...")
        periodic_inspections = []
        
        for i in range(8):
            inspection_id = f'PI-2025-{str(i+1).zfill(3)}'
            project = projects[i % len(projects)]
            person = personnel[i % len(personnel)]
            
            plan_start_date = base_date + timedelta(days=i*10)
            plan_end_date = plan_start_date + timedelta(days=7)
            
            periodic_inspections.append((
                inspection_id,
                project[0],
                project[1],
                plan_start_date,
                plan_end_date,
                project[5],
                person[0],
                random.choice(['待执行', '进行中', '已完成', '已延期']),
                f'定期巡检第{i+1}期，重点关注设备运行状态'
            ))
        
        for inspection in periodic_inspections:
            cursor.execute("""
                INSERT INTO periodic_inspection (inspection_id, project_id, project_name, plan_start_date, plan_end_date,
                                              client_name, maintenance_personnel, status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, inspection)
        
        print(f"✅ 插入了 {len(periodic_inspections)} 条定期巡检")
        print()
        
        # 插入巡检事项
        print("📝 正在插入巡检事项...")
        inspection_items = [
            ('II-2025-001', '电梯系统', '电梯', '检查电梯运行状态，测试安全装置', '符合GB7588-2003标准'),
            ('II-2025-002', '消防系统', '消防', '检查消防设备完好性，测试报警系统', '符合GB50166-2007标准'),
            ('II-2025-003', '空调系统', '空调', '检查空调运行效果，清洁滤网', '符合GB50189-2015标准'),
            ('II-2025-004', '电力系统', '电力', '检查线路安全，测试配电设备', '符合GB50052-2009标准'),
            ('II-2025-005', '给排水系统', '给排水', '检查管道通畅性，测试水泵', '符合GB50015-2003标准'),
            ('II-2025-006', '安防系统', '安防', '检查监控设备，测试门禁系统', '符合GB50348-2004标准'),
        ]
        
        for item in inspection_items:
            cursor.execute("""
                INSERT INTO inspection_item (item_code, item_name, item_type, check_content, check_standard)
                VALUES (%s, %s, %s, %s, %s)
            """, item)
        
        print(f"✅ 插入了 {len(inspection_items)} 条巡检事项")
        print()
        
        # 验证数据
        print("📊 正在验证数据...")
        cursor.execute("SELECT COUNT(*) FROM project_info;")
        project_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM personnel;")
        personnel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM maintenance_plan;")
        plan_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM periodic_inspection;")
        inspection_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inspection_item;")
        item_count = cursor.fetchone()[0]
        
        print(f"✅ 项目信息: {project_count} 条")
        print(f"✅ 人员信息: {personnel_count} 条")
        print(f"✅ 维保计划: {plan_count} 条")
        print(f"✅ 定期巡检: {inspection_count} 条")
        print(f"✅ 巡检事项: {item_count} 条")
        print()
        
        print("🎉 测试数据插入完成！")
        print()
        print("现在您可以：")
        print("1. 访问前端页面查看数据: http://localhost:3000")
        print("2. 访问 API 文档: http://localhost:8080/docs")
        print("3. 测试增删改查功能")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    insert_test_data()
