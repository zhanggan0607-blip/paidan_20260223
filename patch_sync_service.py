"""
Patch script to fix sync_service.py on remote server
"""
import re

file_path = '/opt/sstcp/backend-python/app/services/sync_service.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_text = """        if maintenance_plan.project:
            if not project_name:
                project_name = maintenance_plan.project.project_name
            client_name = maintenance_plan.project.client_name or ''

        if existing_plan:"""

new_text = """        if maintenance_plan.project:
            if not project_name:
                project_name = maintenance_plan.project.project_name
            client_name = maintenance_plan.project.client_name or ''

        if not project_name:
            from app.models.project_info import ProjectInfo
            project = self.db.query(ProjectInfo).filter(
                ProjectInfo.project_id == maintenance_plan.project_id
            ).first()
            if project:
                project_name = project.project_name or maintenance_plan.project_id
                client_name = project.client_name or ''
            else:
                project_name = maintenance_plan.project_id
                logger.warning(f'未找到项目信息，使用project_id作为project_name: {maintenance_plan.project_id}')

        if existing_plan:"""

content = content.replace(old_text, new_text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('File updated successfully')
