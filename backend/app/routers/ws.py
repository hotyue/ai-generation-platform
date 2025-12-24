from fastapi import APIRouter, WebSocket
import os
import jwt

from backend.app.models.user import User
from backend.app.database import SessionLocal
from backend.app.ws.account_status import _run_user_ws_session  # 统一会话实现

router = APIRouter()

# 运行期读取 JWT 密钥
JWT_SECRET = os.getenv("JWT_SECRET")


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """
    v1.0.21
    /ws 作为 user-level WS 主入口
    - WS 内鉴权（与 /ws/account-status 同构）
    - 不使用 Depends / HTTPBearer
    - 失败统一 websocket.close()
    """

    # 1) 读取 token
    token = websocket.query_params.get("token")
    if not token or not JWT_SECRET:
        await websocket.close()
        return

    # 2) JWT 鉴权
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close()
        return

    # 3) 加载用户
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close()
            return
    finally:
        db.close()

    # 4) 进入统一 WS 会话
    await _run_user_ws_session(websocket, user)
