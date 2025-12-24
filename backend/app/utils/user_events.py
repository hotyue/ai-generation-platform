import uuid
import time
import logging
import asyncio
import anyio

from backend.app.ws.manager import manager

logger = logging.getLogger(__name__)


def build_quota_event(user_id: int, balance: int) -> dict:
    """
    v1.0.17 · quota WS 统一事件外壳
    - 保持 USER_QUOTA_UPDATED 语义不变
    - 保持 payload.balance 不变
    """
    return {
        "event_id": uuid.uuid4().hex,
        "event_type": "USER_QUOTA_UPDATED",
        "timestamp": int(time.time()),
        "version": "v1.0.17",
        "payload": {
            "balance": balance,
        },
    }


def emit_user_quota_event(user_id: int, balance: int):
    """
    v1.0.16 → v1.0.17：
    - quota WS 的唯一合法出口
    - 兼容 sync / async 调用环境
    - 以“最终落账事实”为推送依据
    - 仅调整事件协议外壳，不改变并发模型
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
