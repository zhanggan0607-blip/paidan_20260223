#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 TQ-2024-004A-SH 项目在三个表中的数据情况
"""
import psycopg2

def main():
    conn = psycopg2.connect(
        host='pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com',
        port=5432,
        database='tq',
        user='zhanggan',
        password='Lily421020#'
    )
    
    cur = conn.cursor()
    
    print('=' * 80)
    print('1. maintenance_plan 表中 TQ-2024-004A-SH 项目的记录:')
    print('=' * 80)
    cur.execute("""
        SELECT plan_id, project_id, plan_name, plan_type, status, is_deleted, created_at
        FROM maintenance_plan 
        WHERE project_id LIKE '%004A-SH%'
        ORDER BY id DESC
    """)
    maintenance_rows = cur.fetchall()
    for row in maintenance_rows:
        print(f'  plan_id: {row[0]}, project_id: {row[1]}, plan_type: {row[3]}, status: {row[4]}, is_deleted: {row[5]}')
    
    print()
    print('=' * 80)
    print('2. periodic_inspection 表中 TQ-2024-004A-SH 项目的工单:')
    print('=' * 80)
    cur.execute("""
        SELECT inspection_id, project_id, project_name, status, is_deleted, created_at
        FROM periodic_inspection 
        WHERE project_id LIKE '%004A-SH%'
        ORDER BY id DESC
    """)
    inspection_rows = cur.fetchall()
    for row in inspection_rows:
        print(f'  inspection_id: {row[0]}, project_id: {row[1]}, project_name: {row[2]}, status: {row[3]}, is_deleted: {row[4]}')
    
    print()
    print('=' * 80)
    print('4. 检查 project_info 表中 TQ-2024-004A-SH 项目的信息:')
    print('=' * 80)
    cur.execute("""
        SELECT project_id, project_name, client_name
        FROM project_info 
        WHERE project_id LIKE '%004A-SH%'
    """)
    project_rows = cur.fetchall()
    for row in project_rows:
        print(f'  project_id: {row[0]}, project_name: {row[1]}, client_name: {row[2]}')
    
    print()
    print('=' * 80)
    print('3. work_plan 表中 TQ-2024-004A-SH 项目的记录:')
    print('=' * 80)
    cur.execute("""
        SELECT plan_id, project_id, plan_name, plan_type, status, is_deleted, created_at
        FROM work_plan 
        WHERE project_id LIKE '%004A-SH%'
        ORDER BY id DESC
    """)
    work_plan_rows = cur.fetchall()
    for row in work_plan_rows:
        print(f'  plan_id: {row[0]}, project_id: {row[1]}, plan_type: {row[3]}, status: {row[4]}, is_deleted: {row[5]}')
    
    print()
    print('=' * 80)
    print('统计汇总:')
    print('=' * 80)
    print(f'  maintenance_plan 表记录数: {len(maintenance_rows)}')
    print(f'  periodic_inspection 表记录数: {len(inspection_rows)}')
    print(f'  work_plan 表记录数: {len(work_plan_rows)}')
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
