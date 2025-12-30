# backend/app/services/honor_facts_advancer.py

import time
import logging
import random
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.app.database import SessionLocal
from backend.app.models.history import History
from backend.app.models.user import User
from backend.app.models.honor_level_event import HonorLevelEvent
from backend.app.models.quota_log import QuotaLog  # ✅ 奖励流水写入 quota_logs
from backend.app.ws.manager import manager  # ✅ 使用线程安全投递接口（关键修复）

logger = logging.getLogger(__name__)

SCAN_INTERVAL_SECONDS = 3


# =========================
# Step 8.2 · 等级计算函数
# =========================
def calculate_levels_from_tasks(total_success_tasks: int):
    """
    按裁决规则：
    - 每 10 次成功 = 1 level
    - 五进制拆分到 star / moon / sun / diamond / crown
    """
    level = total_success_tasks // 10

    star = level % 5
    level //= 5

    moon = level % 5
    level //= 5

    sun = level % 5
    level //= 5

    diamond = level % 5
    level //= 5

    crown = level % 5

    return star, moon, sun, diamond, crown


def _level_int(star: int, moon: int, sun: int, diamond: int, crown: int) -> int:
    """
    将五进制组件还原为整数等级（仅用于 WS 展示语义，不改变任何规则与落库事实）
    level = crown*5^4 + diamond*5^3 + sun*5^2 + moon*5 + star
    """
    return (((crown * 5 + diamond) * 5 + sun) * 5 + moon) * 5 + star


def _build_quota_event(user_id: int, balance: int) -> dict:
    """
    保持既有 WS 协议：
    - event_type: USER_QUOTA_UPDATED
    - payload.balance: int
    """
    return {
        "event_id": uuid.uuid4().hex,
        "event_type": "USER_QUOTA_UPDATED",
        "payload": {"balance": int(balance)},
        "timestamp": int(time.time()),
        "version": "v1.0.17",
    }


def _build_honor_level_up_event(payload: dict) -> dict:
    return {
        "event_id": uuid.uuid4().hex,
        "event_type": "HONOR_LEVEL_UP",
        "payload": payload,
        "timestamp": int(time.time()),
        "version": "v1.0.30",
    }


def advance_honor_facts_once(db: Session):
    """
    v1.0.30 · Honor Facts Advancer

    关键修复裁决与控制流程（你指定的“等级向上提”）：
    1) level 达到升级条件（after_tasks // 10 > before_tasks // 10）裁决成立
    2) level 升级回写（users.level_*，五档展示值）
    3) 系统奖励回写（users.quota + quota_logs）
    4) 事件回写（honor_level_events：accumulate + level_up）
    5) 单次 commit 成功后，再发送 WS：
       - USER_QUOTA_UPDATED（payload.balance）
       - HONOR_LEVEL_UP（升级语义 + 奖励语义 + 五档展示值）
    """

    logger.debug("[honor-advancer] scan begin")

    candidates = (
        db.query(History)
        .filter(
            and_(
                History.status == "success",
                History.image_url.isnot(None),
                History.honor_consumed_at.is_(None),
            )
        )
        .order_by(History.created_at.asc())
        .limit(5)
        .all()
    )

    if not candidates:
        logger.debug("[honor-advancer] no candidates")
        return

    for c in candidates:
        try:
            # ---------- 锁 history ----------
            h = (
                db.query(History)
                .filter(History.id == c.id)
                .with_for_update()
                .one()
            )

            if h.honor_consumed_at is not None:
                db.rollback()
                continue

            if h.status != "success" or not h.image_url:
                db.rollback()
                continue

            # ---------- 锁 user ----------
            user = (
                db.query(User)
                .filter(User.id == h.user_id)
                .with_for_update()
                .one()
            )

            # =========================
            # 事实裁决点（等级向上提）
            # =========================
            before_tasks = int(user.total_success_tasks or 0)
            after_tasks = before_tasks + 1

            before_task_level = before_tasks // 10
            after_task_level = after_tasks // 10
            is_level_up = after_task_level > before_task_level

            # 五档展示值：严格按规则重算（前端只展示，不计算）
            (before_star, before_moon, before_sun, before_diamond, before_crown) = calculate_levels_from_tasks(before_tasks)
            (after_star, after_moon, after_sun, after_diamond, after_crown) = calculate_levels_from_tasks(after_tasks)

            before_quota = int(user.quota or 0)
            reward = 0
            after_quota = before_quota

            # =========================
            # Step 6.1（事实回写）
            # =========================
            h.honor_consumed_at = datetime.utcnow()  # ✅ UTC
            user.total_success_tasks = after_tasks
            user.user_fact_consumed_at = datetime.utcnow()  # ✅ UTC

            # Step 8.2（五档显示值回写）
            user.level_star = after_star
            user.level_moon = after_moon
            user.level_sun = after_sun
            user.level_diamond = after_diamond
            user.level_crown = after_crown

            # Step 8.1（累计事实事件：不再作为闸门）
            accumulate_event = HonorLevelEvent(
                user_id=user.id,
                trigger="success_task_accumulate",

                before_total_success_tasks=before_tasks,
                after_total_success_tasks=after_tasks,

                before_star=before_star,
                after_star=after_star,

                before_moon=before_moon,
                after_moon=after_moon,

                before_sun=before_sun,
                after_sun=after_sun,

                before_diamond=before_diamond,
                after_diamond=after_diamond,

                before_crown=before_crown,
                after_crown=after_crown,

                reward_quota_delta=0,
                created_at=datetime.utcnow(),  # ✅ UTC
            )

            db.add(h)
            db.add(user)
            db.add(accumulate_event)

            # =========================
            # Step 8.3 + Step 9（升级成立 → 奖励/日志回写）
            # =========================
            if is_level_up:
                reward = random.randint(1, 3)
                after_quota = before_quota + reward
                user.quota = after_quota

                level_up_event = HonorLevelEvent(
                    user_id=user.id,
                    trigger="level_up",

                    before_total_success_tasks=before_tasks,
                    after_total_success_tasks=after_tasks,

                    before_star=before_star,
                    after_star=after_star,

                    before_moon=before_moon,
                    after_moon=after_moon,

                    before_sun=before_sun,
                    after_sun=after_sun,

                    before_diamond=before_diamond,
                    after_diamond=after_diamond,

                    before_crown=before_crown,
                    after_crown=after_crown,

                    reward_quota_delta=reward,
                    created_at=datetime.utcnow(),  # ✅ UTC
                )

                reward_log = QuotaLog(
                    user_id=user.id,
                    change=reward,
                    reason="荣誉升级奖励",
                    operator_id=None,
                    related_plan_id=None,
                    created_at=datetime.utcnow(),  # ✅ UTC
                )

                db.add(level_up_event)
                db.add(reward_log)

            # =========================
            # 单次提交：确保事实一致落库
            # =========================
            db.commit()

            logger.info(
                "[honor-advancer] consumed history=%s user=%s tasks %s->%s task_level %s->%s level_up=%s",
                h.id,
                user.id,
                before_tasks,
                after_tasks,
                before_task_level,
                after_task_level,
                is_level_up,
            )

            # =========================
            # WS 推送（commit 成功后）
            # =========================
            # 注意：只有“升级成立”才发 HONOR_LEVEL_UP；余额事件也只在升级奖励发生时发（避免无意义噪声）
            if is_level_up:
                # 1) 余额 WS（保持旧协议 payload.balance）
                quota_event = _build_quota_event(user.id, int(user.quota or 0))
                sent_quota = manager.send_to_user_threadsafe(user.id, quota_event)

                # 2) 荣誉升级 WS（独立事件）
                before_level_int = _level_int(before_star, before_moon, before_sun, before_diamond, before_crown)
                after_level_int = _level_int(after_star, after_moon, after_sun, after_diamond, after_crown)

                honor_payload = {
                    "reward_quota": reward,

                    # 业务升级：严格按 //10
                    "task_level_before": before_task_level,
                    "task_level_after": after_task_level,
                    "task_level_delta": after_task_level - before_task_level,

                    # 图形等级：用于前端展示
                    "level_before": before_level_int,
                    "level_after": after_level_int,
                    "level_delta": after_level_int - before_level_int,

                    "before": {
                        "star": before_star,
                        "moon": before_moon,
                        "sun": before_sun,
                        "diamond": before_diamond,
                        "crown": before_crown,
                    },
                    "after": {
                        "star": after_star,
                        "moon": after_moon,
                        "sun": after_sun,
                        "diamond": after_diamond,
                        "crown": after_crown,
                    },

                    "before_total_success_tasks": before_tasks,
                    "after_total_success_tasks": after_tasks,

                    # 冗余余额（前端可用单事件完成提示条展示）
                    "balance": int(user.quota or 0),
                }

                honor_event = _build_honor_level_up_event(honor_payload)
                sent_honor = manager.send_to_user_threadsafe(user.id, honor_event)

                logger.info(
                    "[honor-advancer] ws_sent user=%s quota=%s honor=%s",
                    user.id,
                    sent_quota,
                    sent_honor,
                )

        except Exception:
            db.rollback()
            logger.exception(
                "[honor-advancer] error processing history %s",
                getattr(c, "id", None),
            )


def honor_facts_advancer_loop():
    """
    Honor Facts Advancer 后台主循环
    """
    logger.info("[honor-advancer] honor facts advancer started")

    while True:
        db = SessionLocal()
        try:
            advance_honor_facts_once(db)
        except Exception:
            logger.exception("[honor-advancer] fatal loop error")
        finally:
            db.close()

        time.sleep(SCAN_INTERVAL_SECONDS)
