"""
数据一致性检查和同步脚本
检查所有关联表与project_info表的数据一致性，并同步更新
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.database import engine
from sqlalchemy import text, inspect


def get_table_columns(connection, table_name: str) -> list:
    """获取表的列名列表"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return columns


def check_and_sync():
    """检查并同步数据一致性"""
    with engine.connect() as conn:
        print("=" * 60)
        print("数据一致性检查和同步脚本")
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 获取所有项目信息
        projects_result = conn.execute(text("""
            SELECT project_id, project_name, client_name, address, 
                   client_contact, client_contact_info
            FROM project_info
        """))
        projects = {row.project_id: row._asdict() for row in projects_result}
        
        print(f"\n项目信息表共有 {len(projects)} 条记录")
        
        # 定义需要检查的关联表
        related_tables = [
            {
                'name': 'periodic_inspection',
                'project_id_field': 'project_id',
                'sync_fields': {
                    'project_name': 'project_name',
                    'client_name': 'client_name'
                }
            },
            {
                'name': 'temporary_repair',
                'project_id_field': 'project_id',
                'sync_fields': {
                    'project_name': 'project_name',
                    'client_name': 'client_name'
                }
            },
            {
                'name': 'spot_work',
                'project_id_field': 'project_id',
                'sync_fields': {
                    'project_name': 'project_name',
                    'client_name': 'client_name'
                }
            },
            {
                'name': 'maintenance_plan',
                'project_id_field': 'project_id',
                'sync_fields': {
                    'project_name': 'project_name'
                }
            },
            {
                'name': 'work_plan',
                'project_id_field': 'project_id',
                'sync_fields': {
                    'project_name': 'project_name',
                    'client_name': 'client_name',
                    'address': 'address'
                }
            }
        ]
        
        total_issues = 0
        total_fixed = 0
        
        for table_info in related_tables:
            table_name = table_info['name']
            project_id_field = table_info['project_id_field']
            sync_fields = table_info['sync_fields']
            
            print(f"\n{'=' * 50}")
            print(f"检查表: {table_name}")
            print(f"{'=' * 50}")
            
            # 获取表的所有列
            table_columns = get_table_columns(conn, table_name)
            
            # 过滤出实际存在的同步字段
            actual_sync_fields = {k: v for k, v in sync_fields.items() if v in table_columns}
            
            if not actual_sync_fields:
                print(f"  表 {table_name} 没有需要同步的字段，跳过")
                continue
            
            # 检查是否存在project_id字段
            if project_id_field not in table_columns:
                print(f"  表 {table_name} 没有 {project_id_field} 字段，跳过")
                continue
            
            # 查询所有记录
            select_fields = [project_id_field] + list(actual_sync_fields.keys())
            select_sql = f"SELECT id, {', '.join(select_fields)} FROM {table_name}"
            
            try:
                result = conn.execute(text(select_sql))
                records = result.fetchall()
            except Exception as e:
                print(f"  查询表 {table_name} 失败: {e}")
                continue
            
            print(f"  表中共有 {len(records)} 条记录")
            
            issues = []
            
            for record in records:
                record_dict = record._asdict()
                record_id = record_dict['id']
                project_id = record_dict[project_id_field]
                
                # 检查project_id是否存在
                if project_id not in projects:
                    issues.append({
                        'id': record_id,
                        'type': 'missing_project',
                        'message': f"project_id '{project_id}' 在project_info表中不存在"
                    })
                    continue
                
                project = projects[project_id]
                
                # 检查各字段是否一致
                for src_field, dst_field in actual_sync_fields.items():
                    record_value = record_dict.get(src_field, '')
                    project_value = project.get(src_field, '') or ''
                    
                    if record_value != project_value:
                        issues.append({
                            'id': record_id,
                            'type': 'mismatch',
                            'field': src_field,
                            'record_value': record_value,
                            'project_value': project_value,
                            'project_id': project_id
                        })
            
            if issues:
                print(f"\n  发现 {len(issues)} 个问题:")
                total_issues += len(issues)
                
                # 按类型分组显示
                missing_projects = [i for i in issues if i['type'] == 'missing_project']
                mismatches = [i for i in issues if i['type'] == 'mismatch']
                
                if missing_projects:
                    print(f"\n  ⚠ 缺失项目引用 ({len(missing_projects)} 条):")
                    for issue in missing_projects[:5]:
                        print(f"    - ID {issue['id']}: {issue['message']}")
                    if len(missing_projects) > 5:
                        print(f"    ... 还有 {len(missing_projects) - 5} 条")
                
                if mismatches:
                    print(f"\n  ⚠ 字段不一致 ({len(mismatches)} 条):")
                    # 按字段分组
                    field_issues = {}
                    for issue in mismatches:
                        field = issue['field']
                        if field not in field_issues:
                            field_issues[field] = []
                        field_issues[field].append(issue)
                    
                    for field, field_issue_list in field_issues.items():
                        print(f"    字段 '{field}': {len(field_issue_list)} 条不一致")
                        for issue in field_issue_list[:3]:
                            print(f"      - ID {issue['id']}: '{issue['record_value']}' -> '{issue['project_value']}'")
                        if len(field_issue_list) > 3:
                            print(f"      ... 还有 {len(field_issue_list) - 3} 条")
                
                # 执行同步修复
                print(f"\n  开始同步修复...")
                fixed_count = 0
                
                for issue in mismatches:
                    try:
                        update_sql = f"""
                            UPDATE {table_name} 
                            SET {issue['field']} = :value 
                            WHERE id = :id
                        """
                        conn.execute(text(update_sql), {
                            'value': issue['project_value'],
                            'id': issue['id']
                        })
                        fixed_count += 1
                    except Exception as e:
                        print(f"    ✗ 修复 ID {issue['id']} 失败: {e}")
                
                conn.commit()
                print(f"  ✓ 已修复 {fixed_count} 条记录")
                total_fixed += fixed_count
                
                # 对于缺失项目引用的记录，给出警告
                if missing_projects:
                    print(f"\n  ⚠ 注意: {len(missing_projects)} 条记录的project_id在project_info表中不存在")
                    print(f"    建议检查这些记录是否需要删除或更新project_id")
            else:
                print(f"  ✓ 数据一致，无需修复")
        
        # 汇总报告
        print(f"\n{'=' * 60}")
        print("检查完成汇总")
        print(f"{'=' * 60}")
        print(f"发现问题总数: {total_issues}")
        print(f"已修复记录数: {total_fixed}")
        
        # 检查是否有孤立的project_id
        print(f"\n{'=' * 60}")
        print("检查孤立项目")
        print(f"{'=' * 60}")
        
        for table_info in related_tables:
            table_name = table_info['name']
            project_id_field = table_info['project_id_field']
            
            try:
                result = conn.execute(text(f"""
                    SELECT DISTINCT {project_id_field} 
                    FROM {table_name} 
                    WHERE {project_id_field} NOT IN (SELECT project_id FROM project_info)
                """))
                orphan_ids = [row[0] for row in result.fetchall()]
                
                if orphan_ids:
                    print(f"\n  表 {table_name} 中有 {len(orphan_ids)} 个孤立的project_id:")
                    for pid in orphan_ids[:5]:
                        print(f"    - {pid}")
                    if len(orphan_ids) > 5:
                        print(f"    ... 还有 {len(orphan_ids) - 5} 个")
            except Exception as e:
                pass
        
        print(f"\n{'=' * 60}")
        print("脚本执行完成")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    check_and_sync()
