from fastapi import APIRouter, WebSocket
import os
import asyncio
from starlette.websockets import WebSocketDisconnect

from backend.app.models.user import User
from backend.app.database import SessionLocal
from backend.app.ws.manager import manager
from backend.app.ws.events import build_user_ws_event  # ⭐ v1.0.17
from backend.app.ws.versioning import extract_ws_protocol_version  # ⭐ v1.0.18 Phase 2.1
from backend.app.ws.session_state import WSSessionState  # ⭐ v1.0.18 Phase 2.2
from backend.app.ws.system_events import build_system_ws_event  # ⭐ v1.0.18 Phase 2.3
from backend.app.ws.auth import authenticate_ws_user  # ⭐ v1.0.22 统一 WS 鉴权
from backend.app.ws.decision_state import get_current_decision, update_current_decision
from backend.app.services.comfy_event_writer import compute_ws_decision

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
    # v1.0.32：WS 建立成功 → 必须立即推送一次裁决 X/Y/Z
    # 若当前还没有裁决快照，则现场计算一次并写入快照后推送
    # =========================
    try:
        decision = get_current_decision()
        if decision is None:
            db = SessionLocal()
            try:
                decision = compute_ws_decision(db)
                update_current_decision(decision)
            finally:
                db.close()

        if decision is not None:
            await manager.send_to_user(user.id, decision)
    except Exception:
        # 推送失败不影响 WS 会话建立
        pass

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

    last_decision = None

    try:
        while True:
            # 1) 保活：不允许永久阻塞，否则无法持续推送系统级裁决
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                break

            # 2) 裁决变化推送：只读快照，不重新计算
            try:
                current = get_current_decision()
                if current is not None and current != last_decision:
                    await manager.send_to_user(user.id, current)
                    last_decision = current
            except Exception:
                # 推送失败不影响会话
                pass
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
