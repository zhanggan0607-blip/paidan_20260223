from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user_dashboard_config import UserDashboardConfig
import logging

logger = logging.getLogger(__name__)


class UserDashboardConfigRepository:
    def __init__(self, db: Session):
        self._db = db
    
    @property
    def db(self):
        return self._db

    def find_by_user_and_type(self, user_id: str, dashboard_type: str) -> Optional[UserDashboardConfig]:
        try:
            return self.db.query(UserDashboardConfig).filter(
                UserDashboardConfig.user_id == user_id,
                UserDashboardConfig.dashboard_type == dashboard_type
            ).first()
        except Exception as e:
            logger.error(f"查询用户仪表板配置失败 (user_id={user_id}, dashboard_type={dashboard_type}): {str(e)}")
            raise

    def find_all_by_user(self, user_id: str) -> List[UserDashboardConfig]:
        try:
            return self.db.query(UserDashboardConfig).filter(
                UserDashboardConfig.user_id == user_id
            ).all()
        except Exception as e:
            logger.error(f"查询用户所有仪表板配置失败 (user_id={user_id}): {str(e)}")
            raise

    def create(self, config: UserDashboardConfig) -> UserDashboardConfig:
        try:
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            return config
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建用户仪表板配置失败: {str(e)}")
            raise

    def update(self, config: UserDashboardConfig) -> UserDashboardConfig:
        try:
            self.db.commit()
            self.db.refresh(config)
            return config
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户仪表板配置失败: {str(e)}")
            raise

    def delete(self, config: UserDashboardConfig) -> None:
        try:
            self.db.delete(config)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户仪表板配置失败: {str(e)}")
            raise
