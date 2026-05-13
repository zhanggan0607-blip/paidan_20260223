"""
在线用户Repository
提供在线用户相关的数据库操作
"""
from datetime import datetime

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.online_user import OnlineUser
from app.repositories.base import BaseRepository


class OnlineUserRepository(BaseRepository[OnlineUser]):
    def __init__(self, db: Session):
        super().__init__(db, OnlineUser)

    def find_active_by_user_id(self, user_id: int) -> OnlineUser | None:
        return self.db.query(OnlineUser).filter(
            and_(
                OnlineUser.user_id == user_id,
                OnlineUser.is_active == True
            )
        ).first()

    def count_online(self) -> int:
        return self.db.query(func.count(OnlineUser.id)).filter(
            OnlineUser.is_active == True
        ).scalar() or 0

    def get_online_users(self) -> list[OnlineUser]:
        return self.db.query(OnlineUser).filter(
            OnlineUser.is_active == True
        ).order_by(OnlineUser.login_time.desc()).all()

    def get_online_statistics(self) -> dict:
        total_online = self.count_online()
        h5_count = self.db.query(func.count(OnlineUser.id)).filter(
            and_(OnlineUser.is_active == True, OnlineUser.device_type == "h5")
        ).scalar() or 0
        pc_count = self.db.query(func.count(OnlineUser.id)).filter(
            and_(OnlineUser.is_active == True, OnlineUser.device_type == "pc")
        ).scalar() or 0
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logins = self.db.query(func.count(OnlineUser.id)).filter(
            OnlineUser.login_time >= today_start
        ).scalar() or 0
        return {
            "total_online": total_online,
            "h5_count": h5_count,
            "pc_count": pc_count,
            "today_logins": today_logins
        }

    def upsert_online_user(self, user_id: int, user_name: str, ip_address: str, device_type: str) -> None:
        now = datetime.utcnow()
        existing = self.find_active_by_user_id(user_id)
        if existing:
            existing.last_activity = now
            existing.login_time = now
            existing.ip_address = ip_address
            existing.device_type = device_type
        else:
            online_user = OnlineUser(
                user_id=user_id,
                user_name=user_name,
                login_time=now,
                last_activity=now,
                ip_address=ip_address,
                device_type=device_type,
                is_active=True
            )
            self.db.add(online_user)

    def set_user_offline(self, user_id: int) -> None:
        existing = self.find_active_by_user_id(user_id)
        if existing:
            existing.is_active = False
