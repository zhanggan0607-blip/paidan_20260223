from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user_dashboard_config import UserDashboardConfig
from app.repositories.user_dashboard_config import UserDashboardConfigRepository


class UserDashboardConfigService:
    def __init__(self, db: Session):
        self.repository = UserDashboardConfigRepository(db)
    
    def get_by_user_and_type(self, user_id: str, dashboard_type: str) -> UserDashboardConfig:
        config = self.repository.find_by_user_and_type(user_id, dashboard_type)
        if not config:
            return self.get_default_config(dashboard_type)
        return config
    
    def get_all_by_user(self, user_id: str) -> List[UserDashboardConfig]:
        return self.repository.find_all_by_user(user_id)
    
    def get_default_config(self, dashboard_type: str) -> UserDashboardConfig:
        """获取默认配置"""
        default_configs = {
            'statistics': {
                'cards': [
                    {'id': 'nearExpiry', 'visible': True, 'position': 0},
                    {'id': 'overdue', 'visible': True, 'position': 1},
                    {'id': 'completed', 'visible': True, 'position': 2},
                    {'id': 'regularInspection', 'visible': True, 'position': 3},
                    {'id': 'temporaryRepair', 'visible': True, 'position': 4},
                    {'id': 'spotWork', 'visible': True, 'position': 5}
                ],
                'charts': [
                    {'id': 'workByPerson', 'visible': True, 'position': 0},
                    {'id': 'inspectionByPerson', 'visible': True, 'position': 1},
                    {'id': 'repairByPerson', 'visible': True, 'position': 2},
                    {'id': 'laborByPerson', 'visible': True, 'position': 3},
                    {'id': 'completionRate', 'visible': True, 'position': 4},
                    {'id': 'topProjects', 'visible': True, 'position': 5}
                ],
                'layout': 'grid'
            }
        }
        
        config_data = default_configs.get(dashboard_type, {})
        
        return UserDashboardConfig(
            user_id='default',
            dashboard_type=dashboard_type,
            config=config_data
        )
    
    def save_config(self, user_id: str, dashboard_type: str, config: dict) -> UserDashboardConfig:
        existing_config = self.repository.find_by_user_and_type(user_id, dashboard_type)
        
        if existing_config:
            existing_config.config = config
            return self.repository.update(existing_config)
        else:
            new_config = UserDashboardConfig(
                user_id=user_id,
                dashboard_type=dashboard_type,
                config=config
            )
            return self.repository.create(new_config)
    
    def delete_config(self, user_id: str, dashboard_type: str) -> None:
        config = self.repository.find_by_user_and_type(user_id, dashboard_type)
        if config:
            self.repository.delete(config)
