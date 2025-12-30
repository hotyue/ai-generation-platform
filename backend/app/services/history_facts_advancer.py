# backend/app/services/history_facts_advancer.py

import time
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.history import History
from backend.app.utils.http_client import call_result

# ⚠️ 用 print 穿透 gunicorn / uvicorn 日志系统
print(">>> HISTORY FACTS ADVANCER MODULE LOADED <<<", flush=True)

logger = logging.getLogger(__name__)

# =========================
# 配置区（集中、可裁决）
# =========================

SCAN_INTERVAL_SECONDS = 3        # 每轮扫描间隔
TIMEOUT_SECONDS = 60             # 超时判定（秒）
BATCH_SIZE = 20                  # 单轮最大处理条目数

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

    pending_items = (
        db.query(History)
        .filter(History.status == "pending")
        .order_by(History.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )

    if not pending_items:
        return

    for h in pending_items:
        try:
            # ---------- 时间防御性处理 ----------
            created_at = h.created_at
            if created_at.tzinfo is not None:
                created_at = created_at.replace(tzinfo=None)

            # ---------- 超时判定 ----------
            if created_at < timeout_at:
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
            # ⚠️ 不在这里写 failed
            # 任何异常交给下一轮或超时处理
            db.rollback()
            logger.warning(
                "[advancer] error processing history id=%s task_id=%s err=%s",
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
