import psycopg2
from datetime import datetime, timedelta
import random

print("=" * 80)
print("维保计划数据同步")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="123456"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n✅ 数据库连接成功\n")
    
    print("=" * 80)
    print("准备同步的维保计划数据")
    print("=" * 80)
    
    maintenance_plans = [
        {
            "plan_id": "WP202401001",
            "plan_name": "电梯年度维保计划",
            "project_id": "PRJ001",
            "plan_type": "定期维保",
            "equipment_id": "EQ-LIFT-001",
            "equipment_name": "1号客梯",
            "equipment_model": "OTIS-2000",
            "equipment_location": "A栋1楼",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-02-15 00:00:00",
            "next_maintenance_date": "2024-03-15 00:00:00",
            "responsible_person": "李明",
            "responsible_department": "设备维保部",
            "contact_info": "13800138001",
            "maintenance_content": "电梯年度全面检查，包括安全装置、控制系统、曳引系统等",
            "maintenance_requirements": "需要停机操作，至少2小时",
            "maintenance_standard": "按照GB7588-2003电梯制造与安装安全规范执行",
            "plan_status": "进行中",
            "execution_status": "部分完成",
            "completion_rate": 50,
            "remarks": "已完成安全装置检查，待完成控制系统检查"
        },
        {
            "plan_id": "WP202401002",
            "plan_name": "空调系统季度维保",
            "project_id": "PRJ001",
            "plan_type": "定期维保",
            "equipment_id": "EQ-AC-001",
            "equipment_name": "中央空调主机",
            "equipment_model": "Carrier-39G",
            "equipment_location": "B栋机房",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-01-20 00:00:00",
            "next_maintenance_date": "2024-04-20 00:00:00",
            "responsible_person": "王强",
            "responsible_department": "暖通维保部",
            "contact_info": "13800138002",
            "maintenance_content": "空调系统季度保养，包括冷凝器清洗、制冷剂检查、滤网更换",
            "maintenance_requirements": "需要专业技术人员操作",
            "maintenance_standard": "按照设备维护手册执行",
            "plan_status": "进行中",
            "execution_status": "已完成",
            "completion_rate": 100,
            "remarks": "第一季度维保已完成"
        },
        {
            "plan_id": "WP202401003",
            "plan_name": "消防系统月度检查",
            "project_id": "PRJ002",
            "plan_type": "定期维保",
            "equipment_id": "EQ-FIRE-001",
            "equipment_name": "消防报警系统",
            "equipment_model": "GST-5000",
            "equipment_location": "各楼层消防控制箱",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-01-10 00:00:00",
            "next_maintenance_date": "2024-02-10 00:00:00",
            "responsible_person": "张伟",
            "responsible_department": "消防安全部",
            "contact_info": "13800138003",
            "maintenance_content": "消防报警系统月度检查，包括探测器测试、报警器测试、联动测试",
            "maintenance_requirements": "不影响正常使用，可在工作日进行",
            "maintenance_standard": "按照GB50166-2019火灾自动报警系统施工及验收规范执行",
            "plan_status": "进行中",
            "execution_status": "进行中",
            "completion_rate": 30,
            "remarks": "已完成1-3楼检查"
        },
        {
            "plan_id": "WP202401004",
            "plan_name": "给排水系统年度维保",
            "project_id": "PRJ003",
            "plan_type": "定期维保",
            "equipment_id": "EQ-WATER-001",
            "equipment_name": "生活水泵",
            "equipment_model": "Grundfos-CH2-30",
            "equipment_location": "地下1层水泵房",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-03-01 00:00:00",
            "next_maintenance_date": "2024-06-01 00:00:00",
            "responsible_person": "刘洋",
            "responsible_department": "给排水维保部",
            "contact_info": "13800138004",
            "maintenance_content": "生活水泵年度保养，包括电机检查、密封件更换、轴承润滑",
            "maintenance_requirements": "需要停水操作，提前通知用户",
            "maintenance_standard": "按照GB50242-2002建筑给水排水及采暖工程施工质量验收规范执行",
            "plan_status": "待执行",
            "execution_status": "未开始",
            "completion_rate": 0,
            "remarks": "等待用户确认停水时间"
        },
        {
            "plan_id": "WP202401005",
            "plan_name": "配电系统季度巡检",
            "project_id": "PRJ001",
            "plan_type": "定期维保",
            "equipment_id": "EQ-ELEC-001",
            "equipment_name": "低压配电柜",
            "equipment_model": "ABB-MNS",
            "equipment_location": "地下1层配电室",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-01-15 00:00:00",
            "next_maintenance_date": "2024-04-15 00:00:00",
            "responsible_person": "陈刚",
            "responsible_department": "电气维保部",
            "contact_info": "13800138005",
            "maintenance_content": "低压配电柜季度巡检，包括接线端子检查、绝缘测试、保护装置测试",
            "maintenance_requirements": "需要停电操作，确保安全",
            "maintenance_standard": "按照GB50054-2011低压配电设计规范执行",
            "plan_status": "进行中",
            "execution_status": "已完成",
            "completion_rate": 100,
            "remarks": "第一季度巡检已完成"
        },
        {
            "plan_id": "WP202401006",
            "plan_name": "安防系统月度维护",
            "project_id": "PRJ002",
            "plan_type": "定期维保",
            "equipment_id": "EQ-SEC-001",
            "equipment_name": "视频监控系统",
            "equipment_model": "Hikvision-DS-2CD",
            "equipment_location": "各楼层及出入口",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-01-05 00:00:00",
            "next_maintenance_date": "2024-02-05 00:00:00",
            "responsible_person": "赵敏",
            "responsible_department": "安防维保部",
            "contact_info": "13800138006",
            "maintenance_content": "视频监控系统月度维护，包括摄像头清洁、录像检查、系统备份",
            "maintenance_requirements": "不影响正常监控，可分区域进行",
            "maintenance_standard": "按照GB50395-2007视频安防监控系统工程设计规范执行",
            "plan_status": "进行中",
            "execution_status": "进行中",
            "completion_rate": 60,
            "remarks": "已完成1-5楼摄像头维护"
        },
        {
            "plan_id": "WP202401007",
            "plan_name": "停车场系统季度保养",
            "project_id": "PRJ004",
            "plan_type": "定期维保",
            "equipment_id": "EQ-PARK-001",
            "equipment_name": "智能停车系统",
            "equipment_model": "捷顺-JS",
            "equipment_location": "地下停车场出入口",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-02-01 00:00:00",
            "next_maintenance_date": "2024-05-01 00:00:00",
            "responsible_person": "孙丽",
            "responsible_department": "弱电维保部",
            "contact_info": "13800138007",
            "maintenance_content": "智能停车系统季度保养，包括道闸检查、车牌识别系统校准、收费系统测试",
            "maintenance_requirements": "尽量在夜间进行，减少对用户影响",
            "maintenance_standard": "按照设备维护手册执行",
            "plan_status": "待执行",
            "execution_status": "未开始",
            "completion_rate": 0,
            "remarks": "等待安排维护时间"
        },
        {
            "plan_id": "WP202401008",
            "plan_name": "照明系统月度巡检",
            "project_id": "PRJ001",
            "plan_type": "定期维保",
            "equipment_id": "EQ-LIGHT-001",
            "equipment_name": "公共区域照明",
            "equipment_model": "LED-Panel",
            "equipment_location": "各楼层公共区域",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-01-08 00:00:00",
            "next_maintenance_date": "2024-02-08 00:00:00",
            "responsible_person": "周杰",
            "responsible_department": "设施维保部",
            "contact_info": "13800138008",
            "maintenance_content": "公共区域照明月度巡检，包括灯具检查、线路检查、更换损坏灯具",
            "maintenance_requirements": "不影响正常使用，可在白天进行",
            "maintenance_standard": "按照GB50034-2013建筑照明设计标准执行",
            "plan_status": "进行中",
            "execution_status": "已完成",
            "completion_rate": 100,
            "remarks": "1月份巡检已完成"
        },
        {
            "plan_id": "WP202401009",
            "plan_name": "门禁系统季度维护",
            "project_id": "PRJ002",
            "plan_type": "定期维保",
            "equipment_id": "EQ-ACCESS-001",
            "equipment_name": "智能门禁系统",
            "equipment_model": "Honeywell-7",
            "equipment_location": "各楼层出入口",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-01-25 00:00:00",
            "next_maintenance_date": "2024-04-25 00:00:00",
            "responsible_person": "吴芳",
            "responsible_department": "安防维保部",
            "contact_info": "13800138009",
            "maintenance_content": "智能门禁系统季度维护，包括读卡器检查、门锁检查、系统权限更新",
            "maintenance_requirements": "不影响正常通行，可分区域进行",
            "maintenance_standard": "按照GB50396-2007出入口控制系统工程设计规范执行",
            "plan_status": "进行中",
            "execution_status": "进行中",
            "completion_rate": 40,
            "remarks": "已完成1-3楼门禁维护"
        },
        {
            "plan_id": "WP202401010",
            "plan_name": "锅炉系统年度大修",
            "project_id": "PRJ003",
            "plan_type": "大修计划",
            "equipment_id": "EQ-BOILER-001",
            "equipment_name": "燃气锅炉",
            "equipment_model": "WNS-2.8",
            "equipment_location": "地下1层锅炉房",
            "plan_start_date": "2024-01-01 00:00:00",
            "plan_end_date": "2024-12-31 00:00:00",
            "execution_date": "2024-06-01 00:00:00",
            "next_maintenance_date": "2024-06-15 00:00:00",
            "responsible_person": "郑华",
            "responsible_department": "暖通维保部",
            "contact_info": "13800138010",
            "maintenance_content": "燃气锅炉年度大修，包括炉膛检查、燃烧器更换、控制系统升级",
            "maintenance_requirements": "需要停暖操作，提前通知用户，安排在夏季进行",
            "maintenance_standard": "按照TSG G0001-2012锅炉安全技术监察规程执行",
            "plan_status": "待执行",
            "execution_status": "未开始",
            "completion_rate": 0,
            "remarks": "等待夏季停暖期执行"
        }
    ]
    
    print(f"\n准备同步 {len(maintenance_plans)} 条维保计划数据\n")
    
    print("=" * 80)
    print("开始同步数据")
    print("=" * 80)
    
    success_count = 0
    error_count = 0
    
    for i, plan in enumerate(maintenance_plans, 1):
        try:
            insert_sql = """
                INSERT INTO maintenance_plan (
                    plan_id, plan_name, project_id, plan_type, equipment_id, equipment_name,
                    equipment_model, equipment_location, plan_start_date, plan_end_date,
                    execution_date, next_maintenance_date, responsible_person, responsible_department,
                    contact_info, maintenance_content, maintenance_requirements, maintenance_standard,
                    plan_status, execution_status, completion_rate, remarks
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (plan_id) DO NOTHING
            """
            
            cursor.execute(insert_sql, (
                plan["plan_id"],
                plan["plan_name"],
                plan["project_id"],
                plan["plan_type"],
                plan["equipment_id"],
                plan["equipment_name"],
                plan["equipment_model"],
                plan["equipment_location"],
                plan["plan_start_date"],
                plan["plan_end_date"],
                plan["execution_date"],
                plan["next_maintenance_date"],
                plan["responsible_person"],
                plan["responsible_department"],
                plan["contact_info"],
                plan["maintenance_content"],
                plan["maintenance_requirements"],
                plan["maintenance_standard"],
                plan["plan_status"],
                plan["execution_status"],
                plan["completion_rate"],
                plan["remarks"]
            ))
            
            print(f"✅ [{i}/{len(maintenance_plans)}] {plan['plan_name']} - {plan['plan_id']}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ [{i}/{len(maintenance_plans)}] {plan['plan_name']} - {plan['plan_id']}")
            print(f"   错误: {e}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("同步结果")
    print("=" * 80)
    print(f"成功: {success_count} 条")
    print(f"失败: {error_count} 条")
    print(f"总计: {len(maintenance_plans)} 条\n")
    
    print("=" * 80)
    print("验证同步结果")
    print("=" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM maintenance_plan")
    total_count = cursor.fetchone()[0]
    print(f"\n表中总记录数: {total_count}\n")
    
    cursor.execute("""
        SELECT plan_id, plan_name, project_id, plan_type, equipment_name, 
               plan_status, execution_status, completion_rate
        FROM maintenance_plan
        ORDER BY id DESC
        LIMIT 10
    """)
    
    recent_records = cursor.fetchall()
    print("最近同步的记录:\n")
    print(f"{'计划编号':<15} {'计划名称':<20} {'项目编号':<10} {'计划类型':<10} {'设备名称':<15} {'计划状态':<10} {'执行状态':<10} {'完成率':<10}")
    print("-" * 110)
    
    for record in recent_records:
        print(f"{record[0]:<15} {record[1]:<20} {record[2]:<10} {record[3]:<10} {record[4]:<15} {record[5]:<10} {record[6]:<10} {record[7]:<10}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ 数据同步完成")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
