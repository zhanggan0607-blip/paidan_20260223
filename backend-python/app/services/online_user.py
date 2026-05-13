"""
在线用户Service
提供在线用户状态管理的业务逻辑
"""
import uuid

from sqlalchemy.orm import Session

from app.repositories.online_user import OnlineUserRepository
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class OnlineUserService:
    def __init__(self, db: Session):
        self._db = db
        self._repo = OnlineUserRepository(db)

    def record_login(self, user_id: int, user_name: str, ip_address: str, device_type: str) -> dict:
        try:
            self._repo.upsert_online_user(user_id, user_name, ip_address, device_type)
            self._db.commit()
            return {"code": 200, "message": "登录记录成功"}
        except Exception as e:
            self._db.rollback()
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 记录登录失败: {str(e)}")
            return {"code": 500, "message": f"记录登录失败，错误ID: {error_id}"}

    def record_logout(self, user_id: int) -> dict:
        try:
            self._repo.set_user_offline(user_id)
            self._db.commit()
            return {"code": 200, "message": "登出记录成功"}
        except Exception as e:
            self._db.rollback()
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 记录登出失败: {str(e)}")
            return {"code": 500, "message": f"记录登出失败，错误ID: {error_id}"}

    def update_heartbeat(self, user_id: int, user_name: str, ip_address: str, device_type: str) -> dict:
        try:
            self._repo.upsert_online_user(user_id, user_name, ip_address, device_type)
            self._db.commit()
            return {"code": 200, "message": "心跳更新成功"}
        except Exception as e:
            self._db.rollback()
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 心跳更新失败: {str(e)}")
            return {"code": 500, "message": f"心跳更新失败，错误ID: {error_id}"}

    def get_online_count(self) -> dict:
        try:
            count = self._repo.count_online()
            return {"code": 200, "message": "获取成功", "data": {"count": count}}
        except Exception as e:
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 获取在线用户数失败: {str(e)}")
            return {"code": 500, "message": f"获取失败，错误ID: {error_id}"}

    def get_online_users(self) -> dict:
        try:
            users = self._repo.get_online_users()
            return {"code": 200, "message": "获取成功", "data": [user.to_dict() for user in users]}
        except Exception as e:
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 获取在线用户列表失败: {str(e)}")
            return {"code": 500, "message": f"获取失败，错误ID: {error_id}"}

    def get_online_statistics(self) -> dict:
        try:
            stats = self._repo.get_online_statistics()
            return {"code": 200, "message": "获取成功", "data": stats}
        except Exception as e:
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 获取在线用户统计失败: {str(e)}")
            return {"code": 500, "message": f"获取失败，错误ID: {error_id}"}

    def get_online_status_map(self, user_ids: list[int]) -> dict[int, dict]:
        from app.models.online_user import OnlineUser
        online_users = self._db.query(OnlineUser).filter(
            OnlineUser.user_id.in_(user_ids),
            OnlineUser.is_active == True
        ).all()
        return {ou.user_id: ou.to_dict() for ou in online_users}
