from fastapi import APIRouter, WebSocket, Depends

from backend.app.routers.auth import get_current_user_ws  # 复用既有 WS 鉴权
from backend.app.ws.account_status import _run_user_ws_session  # Phase 1 统一会话实现

router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(
    websocket: WebSocket,
    user=Depends(get_current_user_ws),
):
    """
    v1.0.18 Phase 1
    /ws 作为 user-level WS 主入口：
    - 不再自持 connect / keepalive / disconnect
    - 统一复用 account-status 的 WS 会话行为
    - 行为与 /ws/account-status 完全一致
    """
    await _run_user_ws_session(websocket, user)
