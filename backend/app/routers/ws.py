from fastapi import APIRouter, WebSocket

from backend.app.ws.account_status import _run_user_ws_session  # 统一会话实现
from backend.app.ws.auth import authenticate_ws_user  # ⭐ v1.0.22 统一 WS 鉴权

router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """
    v1.0.22
    /ws 作为 user-level WS 主入口

    行为约束（保持与 v1.0.21 完全一致）：
    - token 来源：websocket.query_params["token"]
    - JWT 校验算法：HS256
    - 失败语义：await websocket.close(); return
    - 不使用 Depends / HTTPBearer
    """

    # =========================
    # v1.0.22 · 统一 WS 鉴权与用户加载
    # =========================
    user = await authenticate_ws_user(websocket)
    if not user:
        return

    # =========================
    # 进入统一 WS 会话实现
    # =========================
    await _run_user_ws_session(websocket, user)
