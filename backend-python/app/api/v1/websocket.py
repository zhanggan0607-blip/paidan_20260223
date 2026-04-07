"""
WebSocket API端点
用于实时推送用户在线状态
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.logging_config import get_logger
from app.websocket import manager, get_online_users_from_db

logger = get_logger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/online-status")
async def websocket_online_status(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket端点：实时推送用户在线状态
    客户端连接后会收到当前所有在线用户列表
    之后每当有用户上线或下线，都会收到推送
    """
    await manager.connect(websocket)
    try:
        online_users = get_online_users_from_db(db)
        await websocket.send_json({
            "type": "online_users_list",
            "data": {
                "users": online_users,
                "count": len(online_users)
            }
        })

        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data == "refresh":
                    online_users = get_online_users_from_db(db)
                    await websocket.send_json({
                        "type": "online_users_list",
                        "data": {
                            "users": online_users,
                            "count": len(online_users)
                        }
                    })
            except Exception as e:
                logger.debug(f"WebSocket接收消息异常: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)
