"""
WebSocket API端点
用于实时推送用户在线状态
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.auth import decode_jwt_token
from app.database import SessionLocal
from app.utils.logging_config import get_logger
from app.websocket import manager, get_online_users_from_db

logger = get_logger(__name__)

router = APIRouter(tags=["WebSocket"])


def _get_online_users_short_session() -> list[dict]:
    with SessionLocal() as db:
        try:
            return get_online_users_from_db(db)
        except Exception as e:
            logger.error(f"查询在线用户失败: {e}")
            return []


def _authenticate_websocket(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        payload = decode_jwt_token(token)
        if payload and payload.get("sub"):
            return payload
    except Exception as e:
        logger.warning(f"WebSocket认证失败: {e}")
    return None


@router.websocket("/ws/online-status")
async def websocket_online_status(
    websocket: WebSocket,
    token: str | None = Query(None),
):
    """
    WebSocket端点：实时推送用户在线状态
    需要通过query参数传递token进行认证
    """
    user_data = _authenticate_websocket(token)
    if not user_data:
        await websocket.close(code=4001, reason="认证失败，请提供有效的token")
        return

    user_name = user_data.get("sub", "unknown")
    logger.info(f"WebSocket认证成功: user={user_name}")

    await manager.connect(websocket)
    try:
        online_users = _get_online_users_short_session()
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
                    online_users = _get_online_users_short_session()
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
