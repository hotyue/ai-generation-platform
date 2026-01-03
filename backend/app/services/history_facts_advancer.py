# backend/app/services/history_facts_advancer.py

import time
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.history import History
from backend.app.utils.http_client import call_result
from backend.app.config_history_advancer import (
    SCAN_INTERVAL_SECONDS,
    TIMEOUT_SECONDS,
    BATCH_SIZE,
    ARCHIVE_ABSORB_WINDOW_SECONDS,
)


# ⚠️ 用 print 穿透 gunicorn / uvicorn 日志系统
print(">>> HISTORY FACTS ADVANCER MODULE LOADED <<<", flush=True)

logger = logging.getLogger(__name__)

# =========================
# 核心事实推进器（单轮）
# =========================
def advance_pending_histories_once(db: Session):
    """
    扫描并推进 pending 状态的生成任务事实

    判定规则（v1.0.30 裁决）：
    - success：call_result 返回 images 且非空
    - failed：仅由超时触发
    """

    # ✅ 与数据库 timestamp 对齐：全部使用 naive UTC
    now = datetime.utcnow()
    timeout_at = now - timedelta(seconds=TIMEOUT_SECONDS)
    archive_deadline = now - timedelta(seconds=ARCHIVE_ABSORB_WINDOW_SECONDS)

    # =========================
    # 1️⃣ 处理 pending 任务
    # =========================

    pending_items = (
        db.query(History)
        .filter(History.status == "pending")
        .order_by(History.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )

    for h in pending_items:
        try:
            created_at = h.created_at
            if created_at and created_at.tzinfo is not None:
                created_at = created_at.replace(tzinfo=None)

            # ---------- 超时判定 ----------
            if created_at and created_at < timeout_at:
                h.status = "failed"
                db.add(h)
                db.commit()

                logger.info(
                    "[advancer] history id=%s task_id=%s marked FAILED (timeout)",
                    h.id,
                    h.task_id,
                )
                continue

            # ---------- 成功判定 ----------
            result = call_result(h.task_id)
            if not result:
                continue

            images = result.get("images", [])
            if images:
                h.image_url = images[0].get("url")
                h.status = "success"

                db.add(h)
                db.commit()

                logger.info(
                    "[advancer] history id=%s task_id=%s marked SUCCESS",
                    h.id,
                    h.task_id,
                )

        except Exception as e:
            db.rollback()
            logger.warning(
                "[advancer] error processing history id=%s task_id=%s err=%s",
                h.id,
                h.task_id,
                e,
            )

    # =========================
    # 2️⃣ 归档事实吸收扫描（v1.0.31）
    # =========================

    archive_candidates = (
        db.query(History)
        .filter(
            History.status == "success",
            History.archive_url.is_(None),
            History.created_at.isnot(None),
            History.created_at >= archive_deadline,
        )
        .order_by(History.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )

    for h in archive_candidates:
        try:
            result = call_result(h.task_id)
            if not result:
                continue

            images = result.get("images", [])
            if not images:
                continue

            img = images[0]

            if (
                img.get("archive_status") == "success"
                and img.get("archive_url")
                and h.archive_url is None
            ):
                h.archive_url = img.get("archive_url")
                db.add(h)
                db.commit()

                logger.info(
                    "[advancer] history id=%s task_id=%s archive absorbed",
                    h.id,
                    h.task_id,
                )

        except Exception as e:
            db.rollback()
            logger.warning(
                "[advancer] error absorbing archive for history id=%s task_id=%s err=%s",
                h.id,
                h.task_id,
                e,
            )

# =========================
# 后台循环（阻塞式）
# =========================

def history_facts_advancer_loop():
    """
    后台事实推进主循环

    ⚠️ 注意：
    - 函数名必须与 main.py import 完全一致
    - 该函数必须是“阻塞式 while True”
    """

    print(">>> HISTORY FACTS ADVANCER LOOP STARTED <<<", flush=True)
    logger.info("[advancer] history facts advancer started")

    while True:
        db = SessionLocal()
        try:
            advance_pending_histories_once(db)
        except Exception as e:
            logger.exception("[advancer] fatal loop error: %s", e)
        finally:
            db.close()

        time.sleep(SCAN_INTERVAL_SECONDS)
