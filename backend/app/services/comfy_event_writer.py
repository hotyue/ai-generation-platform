import logging
from sqlalchemy import text
from backend.app.database import SessionLocal
from backend.app.ws.decision_state import update_current_decision

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
        if phase in ("bind", "queued"):
            _handle_bind(db, event, payload, ts)
        elif phase == "running":
            _handle_running(db, prompt_id, ts)
        elif phase == "finished":
            _handle_finished(db, prompt_id, payload, ts)
        else:
            logger.warning("unknown comfy event phase: %s", phase)

        db.commit()

        # STEP 3：裁决重算（不推送 WS）
        try:
            decision = compute_ws_decision(db)
            changed = update_current_decision(decision)
            logger.debug(
                "ws decision recomputed after commit: X=%s Y=%s Z=%s",
                decision["X"],
                decision["Y"],
                decision["Z"],
                changed,
            )
        except Exception:
            # 裁决失败不得影响事实写库
            logger.exception("failed to recompute ws decision")

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

def compute_ws_decision(db, recent_n: int = 10):
    """
    WS 裁决计算（v1.0.32 冻结语义）

    X: 当前未完成任务数（finished_at IS NULL）
    Y: 最近 N 条已完成任务的平均执行耗时（秒）
    Z: 预计完成时间（秒） = (X + 1) * Y

    约束：
    - 只读 DB
    - 不裁剪任务
    - 不依赖前端
    """

    # X：未完成任务数（命中 idx_ctm_unfinished）
    x = db.execute(
        text("""
        SELECT COUNT(*)
        FROM compute_task_mappings
        WHERE finished_at IS NULL
        """)
    ).scalar() or 0

    # Y：最近 N 条完成任务的平均执行耗时（命中 idx_ctm_finished_at_desc）
    y = db.execute(
        text("""
        SELECT AVG(EXTRACT(EPOCH FROM (finished_at - started_at)))
        FROM (
            SELECT started_at, finished_at
            FROM compute_task_mappings
            WHERE finished_at IS NOT NULL
            ORDER BY finished_at DESC
            LIMIT :recent_n
        ) t
        """),
        {"recent_n": recent_n},
    ).scalar()

    y = float(y) if y is not None else 0.0

    # Z：冻结公式
    z = (x + 1) * y

    return {
        "X": x,
        "Y": y,
        "Z": z,
    }
