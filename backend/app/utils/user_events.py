import uuid, time, logging, asyncio
from backend.app.ws.manager import manager

logger = logging.getLogger(__name__)

def build_quota_event(user_id: int, balance: int) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "USER_QUOTA_UPDATED",
        "user_id": user_id,
        "timestamp": int(time.time()),
        "version": 1,
        "payload": {"balance": balance}
    }

def emit_user_quota_event(user_id: int, balance: int):
    """
    v1：旁路广播；失败不抛异常
    """
    event = build_quota_event(user_id, balance)
    try:
        # WS 是 async，这里用 create_task 不阻塞主线程
        asyncio.create_task(manager.send_to_user(user_id, event))
        logger.info(f"[USER_EVENT] {event}")
    except Exception as e:
        logger.warning(f"emit_user_quota_event failed: {e}")
