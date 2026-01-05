from fastapi import APIRouter, Request
import logging

from backend.app.services.comfy_event_writer import handle_comfy_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/internal/comfy",
    tags=["Internal-Comfy"]
)


@router.post("/event")
async def receive_comfy_event(request: Request):
    """
    平台侧算力事实事件接收接口
    - 接收事实
    - 写入 compute_task_mappings
    - 不裁决
    - 不抛异常
    """
    try:
        event = await request.json()
        logger.info("platform received comfy event: %s", event)

        handle_comfy_event(event)

    except Exception:
        logger.exception("platform failed to handle comfy event")

    return {"ok": True}
