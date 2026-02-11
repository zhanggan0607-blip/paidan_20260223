import sqlite3
from datetime import datetime

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS project_info")

cursor.execute("""
    CREATE TABLE project_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id VARCHAR(50) NOT NULL UNIQUE,
        project_name VARCHAR(200) NOT NULL,
        completion_date DATETIME NOT NULL,
        maintenance_end_date DATETIME NOT NULL,
        maintenance_period VARCHAR(20) NOT NULL,
        client_name VARCHAR(100) NOT NULL,
        address VARCHAR(200) NOT NULL,
        project_abbr VARCHAR(10),
        client_contact VARCHAR(50),
        client_contact_position VARCHAR(20),
        client_contact_info VARCHAR(50),
        created_at DATETIME,
        updated_at DATETIME
    )
""")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_info_id ON project_info(project_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_info_client_name ON project_info(client_name)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_info_project_name ON project_info(project_name)")

print("✅ 重新创建 project_info 表")

test_projects = [
    {
        "project_id": "P001",
        "project_name": "北京地铁1号线维保项目",
        "completion_date": "2024-01-01 00:00:00",
        "maintenance_end_date": "2024-12-31 00:00:00",
        "maintenance_period": "每月",
        "client_name": "北京地铁运营有限公司",
        "address": "北京市朝阳区建国路88号",
        "project_abbr": "BJM1",
        "client_contact": "张经理",
        "client_contact_position": "运营总监",
        "client_contact_info": "13800138001"
    },
    {
        "project_id": "P002",
        "project_name": "上海地铁2号线维保项目",
        "completion_date": "2024-02-01 00:00:00",
        "maintenance_end_date": "2024-12-31 00:00:00",
        "maintenance_period": "每周",
        "client_name": "上海地铁运营有限公司",
        "address": "上海市浦东新区世纪大道100号",
        "project_abbr": "SHM2",
        "client_contact": "李总监",
        "client_contact_position": "技术总监",
        "client_contact_info": "13800138002"
    },
    {
        "project_id": "P003",
        "project_name": "广州地铁3号线维保项目",
        "completion_date": "2024-03-01 00:00:00",
        "maintenance_end_date": "2024-12-31 00:00:00",
        "maintenance_period": "每季度",
        "client_name": "广州地铁运营有限公司",
        "address": "广州市天河区天河路200号",
        "project_abbr": "GZM3",
        "client_contact": "王经理",
        "client_contact_position": "项目经理",
        "client_contact_info": "13800138003"
    },
    {
        "project_id": "P004",
        "project_name": "深圳地铁4号线维保项目",
        "completion_date": "2024-04-01 00:00:00",
        "maintenance_end_date": "2024-12-31 00:00:00",
        "maintenance_period": "每天",
        "client_name": "深圳地铁运营有限公司",
        "address": "深圳市福田区深南大道300号",
        "project_abbr": "SZM4",
        "client_contact": "赵总监",
        "client_contact_position": "运营总监",
        "client_contact_info": "13800138004"
    },
    {
        "project_id": "P005",
        "project_name": "成都地铁5号线维保项目",
        "completion_date": "2024-05-01 00:00:00",
        "maintenance_end_date": "2024-12-31 00:00:00",
        "maintenance_period": "每半年",
        "client_name": "成都地铁运营有限公司",
        "address": "成都市锦江区人民南路50号",
        "project_abbr": "CDM5",
        "client_contact": "刘经理",
        "client_contact_position": "技术经理",
        "client_contact_info": "13800138005"
    }
]

for project_data in test_projects:
    try:
        cursor.execute(
            "SELECT id FROM project_info WHERE project_id = ?",
            (project_data["project_id"],)
        )
        if cursor.fetchone():
            print(f"项目 {project_data['project_id']} 已存在，跳过")
            continue
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            """INSERT INTO project_info (
                project_id, project_name, completion_date, maintenance_end_date,
                maintenance_period, client_name, address, project_abbr,
                client_contact, client_contact_position, client_contact_info,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_data["project_id"],
                project_data["project_name"],
                project_data["completion_date"],
                project_data["maintenance_end_date"],
                project_data["maintenance_period"],
                project_data["client_name"],
                project_data["address"],
                project_data["project_abbr"],
                project_data["client_contact"],
                project_data["client_contact_position"],
                project_data["client_contact_info"],
                now,
                now
            )
        )
        print(f"✅ 创建项目: {project_data['project_id']} - {project_data['project_name']}")
    except Exception as e:
        print(f"❌ 创建项目 {project_data['project_id']} 失败: {str(e)}")

conn.commit()
print("✅ 成功创建5条项目信息测试数据")
conn.close()