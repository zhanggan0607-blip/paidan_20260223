import os
import psycopg2
import json

conn = psycopg2.connect(os.environ.get('DATABASE_URL', ''))
cur = conn.cursor()
cur.execute("SELECT name, phone, role FROM personnel WHERE role IN ('管理员','部门经理') LIMIT 5")
rows = cur.fetchall()
print(json.dumps([{'name': r[0], 'phone': r[1], 'role': r[2]} for r in rows], ensure_ascii=False))
cur.close()
conn.close()
