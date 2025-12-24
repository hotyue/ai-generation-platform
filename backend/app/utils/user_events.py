import uuid
import time
import logging
import asyncio
import anyio

from backend.app.ws.manager import manager

logger = logging.getLogger(__name__)


def build_quota_event(user_id: int, balance: int) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "USER_QUOTA_UPDATED",
        "user_id": user_id,
        "timestamp": int(time.time()),
        "version": 1,
        "payload": {"balance": balance},
    }


def emit_user_quota_event(user_id: int, balance: int):
    """
    v1.0.16：
    - quota WS 的唯一合法出口
    - 兼容 sync / async 调用环境
    - 以“最终落账事实”为推送依据
    """
    event = build_quota_event(user_id, balance)

    try:
        # 情况 1：当前在 sync 路由 / 线程池中
        # 必须通过 anyio.from_thread.run 进入主事件循环
        anyio.from_thread.run(
            manager.send_to_user,
            user_id,
            event,
        )
        logger.info(f"[USER_EVENT][quota] {event}")

    except RuntimeError:
        # 情况 2：已经在事件循环中（例如 async 上下文）
        try:
            asyncio.create_task(
                manager.send_to_user(user_id, event)
            )
            logger.info(f"[USER_EVENT][quota][async] {event}")
        except Exception as e:
            logger.warning(f"emit_user_quota_event async failed: {e}")

    except Exception as e:
        logger.warning(f"emit_user_quota_event failed: {e}")
