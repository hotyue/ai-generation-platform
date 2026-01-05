import logging
from sqlalchemy import text
from backend.app.database import SessionLocal

logger = logging.getLogger(__name__)


def handle_comfy_event(event: dict):
    """
    平台侧算力事实事件写库入口
    - 只写 compute_task_mappings
    - 不抛异常
    """
    phase = event.get("phase")
    prompt_id = event.get("prompt_id")
    ts = event.get("timestamp")
    payload = event.get("payload") or {}

    if not phase or not prompt_id or not ts:
        logger.warning("invalid comfy event: %s", event)
        return

    db = SessionLocal()
    try:
        if phase == "bind":
            _handle_bind(db, event, payload, ts)
        elif phase == "running":
            _handle_running(db, prompt_id, ts)
        elif phase == "finished":
            _handle_finished(db, prompt_id, payload, ts)
        else:
            logger.warning("unknown comfy event phase: %s", phase)

        db.commit()

    except Exception:
        db.rollback()
        logger.exception("failed to write comfy event")

    finally:
        db.close()


def _handle_bind(db, event, payload, ts):
    db.execute(
        text("""
        INSERT INTO compute_task_mappings
        (task_id, comfy_prompt_id, compute_node, compute_api, queued_at)
        VALUES (:task_id, :prompt_id, :node, :api, to_timestamp(:ts / 1000))
        ON CONFLICT (comfy_prompt_id) DO NOTHING
        """),
        {
            "task_id": payload.get("task_id"),
            "prompt_id": event.get("prompt_id"),
            "node": event.get("compute_node"),
            "api": event.get("source"),
            "ts": ts,
        },
    )


def _handle_running(db, prompt_id, ts):
    db.execute(
        text("""
        UPDATE compute_task_mappings
        SET started_at = COALESCE(started_at, to_timestamp(:ts / 1000)),
            status = CASE
                WHEN status IS NULL OR status = 'queued' THEN 'running'
                ELSE status
            END
        WHERE comfy_prompt_id = :prompt_id
        """),
        {
            "prompt_id": prompt_id,
            "ts": ts,
        },
    )


def _handle_finished(db, prompt_id, payload, ts):
    db.execute(
        text("""
        UPDATE compute_task_mappings
        SET finished_at = COALESCE(finished_at, to_timestamp(:ts / 1000)),
            item_id = COALESCE(item_id, :item_id),
            status = 'finished'
        WHERE comfy_prompt_id = :prompt_id
        """),
        {
            "prompt_id": prompt_id,
            "item_id": payload.get("item_id"),
            "ts": ts,
        },
    )
