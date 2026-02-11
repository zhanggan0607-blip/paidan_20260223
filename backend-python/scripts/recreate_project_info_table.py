import sqlite3

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
conn.close()