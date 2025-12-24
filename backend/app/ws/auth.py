from fastapi import WebSocket
import os
import jwt

from backend.app.models.user import User
from backend.app.database import SessionLocal

# =========================
# JWT 配置（运行期读取）
# =========================
JWT_SECRET = os.getenv("JWT_SECRET")


async def authenticate_ws_user(websocket: WebSocket) -> User | None:
    """
    v1.0.22 · WebSocket 内部统一鉴权与用户加载

    行为约束（与 v1.0.21 / v1.0.11 完全一致）：
    - token 来源：websocket.query_params["token"]
    - JWT 算法：HS256
    - 失败语义：await websocket.close(); return None
    - 不 accept / 不 raise / 不引入新异常
    """

    token = websocket.query_params.get("token")
    if not token or not JWT_SECRET:
        await websocket.close()
        return None

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
        )
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close()
        return None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close()
            return None
        return user
    finally:
        db.close()
