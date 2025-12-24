from fastapi import APIRouter, WebSocket
import os

from backend.app.models.user import User
from backend.app.database import SessionLocal
from backend.app.ws.manager import manager
from backend.app.ws.events import build_user_ws_event  # ⭐ v1.0.17
from backend.app.ws.versioning import extract_ws_protocol_version  # ⭐ v1.0.18 Phase 2.1
from backend.app.ws.session_state import WSSessionState  # ⭐ v1.0.18 Phase 2.2
from backend.app.ws.system_events import build_system_ws_event  # ⭐ v1.0.18 Phase 2.3
from backend.app.ws.auth import authenticate_ws_user  # ⭐ v1.0.22 统一 WS 鉴权

router = APIRouter()


async def _run_user_ws_session(websocket: WebSocket, user: User) -> None:
    """
    v1.0.18 Phase 2.3
    统一 user-level WS 会话行为（在 Phase 2.2 基础上引入 system-level 治理事件）
    - 识别 WS 协议 version（治理级）
    - 会话状态机（CONNECTED → READY → CLOSED）
    - v1：推送 system-level 事件
    - v0：完全无感知
    """

    # =========================
    # WS 协议 version 识别（治理级）
    # =========================
    ws_version = extract_ws_protocol_version(websocket)

    # =========================
    # 会话状态机：CONNECTED
    # =========================
    session_state = WSSessionState.CONNECTED

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
        session_state = WSSessionState.READY

        # =========================
        # system-level 事件：READY
        # 仅 ws_version == 1
        # =========================
        if ws_version == 1:
            try:
                await manager.send_to_user(
                    user.id,
                    build_system_ws_event("SYSTEM_WS_READY"),
                )
            except Exception:
                pass

    except Exception:
        # 维持既有“弱保证”语义：
        # 推送失败不影响会话建立，也不阻断后续保活
        pass

    try:
        while True:
            await websocket.receive_text()  # 保活
    finally:
        # =========================
        # system-level 事件：CLOSED
        # 仅 ws_version == 1
        # =========================
        if ws_version == 1:
            try:
                await manager.send_to_user(
                    user.id,
                    build_system_ws_event("SYSTEM_WS_CLOSED"),
                )
            except Exception:
                pass

        # =========================
        # 会话状态机：CLOSED
        # =========================
        session_state = WSSessionState.CLOSED
        manager.disconnect(user.id, websocket)


@router.websocket("/ws/account-status")
async def account_status_ws(websocket: WebSocket):
    """
    v1.0.22
    /ws/account-status
    - 行为保持不变
    - 内部鉴权与用户加载统一抽取
    """

    user = await authenticate_ws_user(websocket)
    if not user:
        return

    await _run_user_ws_session(websocket, user)
