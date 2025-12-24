from fastapi import APIRouter, WebSocket
import jwt
import os

from backend.app.models.user import User
from backend.app.database import SessionLocal
from backend.app.ws.manager import manager
from backend.app.ws.events import build_user_ws_event  # ⭐ v1.0.17

router = APIRouter()

# =========================
# JWT 配置（运行期读取）
# =========================
JWT_SECRET = os.getenv("JWT_SECRET")


async def _run_user_ws_session(websocket: WebSocket, user: User) -> None:
    """
    v1.0.18 Phase 1：统一 user-level WS 会话行为（最小 diff）
    - connect
    - 连接成功立即推送 ACCOUNT_STATUS_UPDATED（v1.0.17 外壳）
    - keepalive
    - finally disconnect（覆盖 WebSocketDisconnect/其他异常/取消）
    """
    await manager.connect(user.id, websocket)

    # =========================
    # WS 建立成功 → 立即推送当前状态
    # （v1.0.17 统一事件外壳）
    # =========================
    try:
        event = build_user_ws_event(
            event_type="ACCOUNT_STATUS_UPDATED",
            payload={"account_status": user.account_status},
        )
        await manager.send_to_user(user.id, event)
    except Exception:
        # 维持现有“弱保证”语义：推送失败不影响会话建立
        pass

    try:
        while True:
            await websocket.receive_text()  # 保活
    finally:
        manager.disconnect(user.id, websocket)


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

    await _run_user_ws_session(websocket, user)
