# backend/app/ws/events.py

from backend.app.ws.manager import manager

import asyncio
import logging
import time
import uuid

logger = logging.getLogger("ws-events")


def build_user_ws_event(
    *,
    event_type: str,
    payload: dict,
    version: str = "v1.0.17",
) -> dict:
    """
    v1.0.17 · user-level WS 统一事件外壳
    """
    return {
        "event_id": uuid.uuid4().hex,
        "event_type": event_type,
        "timestamp": int(time.time()),
        "version": version,
        "payload": payload,
    }


async def emit_account_status_event(
    user_id: int,
    account_status: str,
):
    """
    v1.0.11
    管理端触发账号状态变更 → WS 推送给前端
    """

    # =========================
    # 🔍 取证日志（关键）
    # =========================
    try:
        logger.warning(
            "[emit_account_status_event] manager_id=%s users=%s",
            id(manager),
            list(manager._users.keys()),
        )
    except Exception as e:
        logger.error("log manager state failed: %s", e)

    # =========================
    # 实际推送（v1.0.17 统一事件外壳）
    # =========================
    try:
        event = build_user_ws_event(
            event_type="ACCOUNT_STATUS_UPDATED",
            payload={
                "account_status": account_status,
            },
        )

        await manager.send_to_user(user_id, event)
    except Exception as e:
        logger.error(
            "emit_account_status_event failed user_id=%s err=%s",
            user_id,
            e,
        )
