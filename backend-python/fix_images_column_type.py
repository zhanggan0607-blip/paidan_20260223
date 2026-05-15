import psycopg2

conn = psycopg2.connect("postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com:5432/tq")
conn.autocommit = True
cur = conn.cursor()

tables_columns = [
    ("maintenance_log", "images"),
    ("weekly_report", "images"),
]

for table_name, column_name in tables_columns:
    cur.execute(f"SELECT pg_typeof({column_name}) FROM {table_name} LIMIT 1")
    row = cur.fetchone()
    print(f"{table_name}.{column_name}: {row[0]}")

    if str(row[0]) == 'text':
        print(f"  Converting {table_name}.{column_name} from text to jsonb...")
        try:
            cur.execute(f"""
                ALTER TABLE {table_name}
                ALTER COLUMN {column_name}
                TYPE jsonb
                USING CASE
                    WHEN {column_name} IS NULL THEN '[]'::jsonb
                    WHEN {column_name} = '' THEN '[]'::jsonb
                    ELSE {column_name}::jsonb
                END
            """)
            print(f"  Successfully converted!")
        except Exception as e:
            print(f"  Error: {e}")

        cur.execute(f"SELECT pg_typeof({column_name}) FROM {table_name} LIMIT 1")
        row = cur.fetchone()
        print(f"  After: {table_name}.{column_name}: {row[0]}")

cur.close()
conn.close()
