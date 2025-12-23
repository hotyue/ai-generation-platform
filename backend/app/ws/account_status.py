from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import jwt
import os

from backend.app.models.user import User
from backend.app.database import SessionLocal
from backend.app.ws.manager import manager

router = APIRouter()

# =========================
# JWT 配置（运行期读取）
# =========================
JWT_SECRET = os.getenv("JWT_SECRET")


@router.websocket("/ws/account-status")
async def account_status_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token or not JWT_SECRET:
        await websocket.close()
        return

    # =========================
    # WS 独立鉴权（v1.0.11）
    # =========================
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
        )
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close()
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close()
            return
    finally:
        db.close()

    await manager.connect(user.id, websocket)

    # =========================
    # WS 建立成功 → 立即推送当前状态
    # =========================
    try:
        await manager.send_to_user(
            user.id,
            {
                "type": "account_status",
                "account_status": user.account_status,
            },
        )
    except Exception:
        pass

    try:
        while True:
            await websocket.receive_text()  # 保活
    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
