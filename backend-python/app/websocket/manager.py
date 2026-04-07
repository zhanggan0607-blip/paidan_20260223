"""
WebSocket连接管理器
用于实时推送用户在线状态
"""
import asyncio
import json
from datetime import datetime
from typing import Optional

from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    WebSocket连接管理器
    管理所有活跃的WebSocket连接，支持广播在线状态变化
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """
        接受新的WebSocket连接
        @param websocket: WebSocket连接对象
        """
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """
        断开WebSocket连接
        @param websocket: WebSocket连接对象
        """
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        广播消息给所有连接的客户端
        @param message: 要发送的消息字典
        """
        if not self.active_connections:
            return

        message_json = json.dumps(message, ensure_ascii=False, default=str)
        disconnected = []

        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.warning(f"发送消息失败: {e}")
                    disconnected.append(connection)

            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

    async def broadcast_online_status(
        self,
        user_id: int,
        user_name: str,
        is_online: bool,
        device_type: Optional[str] = None
    ):
        """
        广播用户在线状态变化
        @param user_id: 用户ID
        @param user_name: 用户名
        @param is_online: 是否在线
        @param device_type: 设备类型
        """
        message = {
            "type": "online_status",
            "data": {
                "user_id": user_id,
                "user_name": user_name,
                "is_online": is_online,
                "device_type": device_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.broadcast(message)
        logger.debug(f"广播在线状态: {user_name} -> {'在线' if is_online else '离线'}")

    async def broadcast_online_users(self, online_users: list[dict]):
        """
        广播所有在线用户列表
        @param online_users: 在线用户列表
        """
        message = {
            "type": "online_users_list",
            "data": {
                "users": online_users,
                "count": len(online_users),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.broadcast(message)


manager = ConnectionManager()


def get_online_users_from_db(db: Session) -> list[dict]:
    """
    从数据库获取所有在线用户
    @param db: 数据库会话
    @return: 在线用户列表
    """
    from app.models.online_user import OnlineUser
    from datetime import timedelta

    ONLINE_TIMEOUT_MINUTES = 5
    timeout_threshold = datetime.utcnow() - timedelta(minutes=ONLINE_TIMEOUT_MINUTES)

    online_users = db.query(OnlineUser).filter(
        OnlineUser.is_active == True,
        OnlineUser.last_activity >= timeout_threshold
    ).all()

    return [
        {
            "user_id": ou.user_id,
            "user_name": ou.user_name,
            "device_type": ou.device_type,
            "is_online": True
        }
        for ou in online_users
    ]
