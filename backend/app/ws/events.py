# backend/app/ws/events.py

from backend.app.ws.manager import manager

import asyncio
import logging

logger = logging.getLogger("ws-events")


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
    # 实际推送
    # =========================
    try:
        await manager.send_to_user(
            user_id,
            {
                "type": "account_status",
                "account_status": account_status,
            },
        )
    except Exception as e:
        logger.error(
            "emit_account_status_event failed user_id=%s err=%s",
            user_id,
            e,
        )
