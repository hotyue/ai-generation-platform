from typing import List
import random

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.history import History
from backend.app.models.user import User
from backend.app.models.quota_log import QuotaLog
from backend.app.routers.auth import get_current_user
from backend.app.schemas.history import HistoryItem
from backend.app.utils.http_client import call_result
from backend.app.utils.honor_level import calculate_honor_levels
from backend.app.utils.honor_judge import is_strength_upgrade

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=List[HistoryItem],
)
def list_history(
    # =========================
    # E2：可选分页参数
    # 不传时 = 完全等价旧行为
    # =========================
    limit: int | None = Query(default=None, ge=1, le=100),
    offset: int | None = Query(default=None, ge=0),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    E1 + E2 阶段：
    - 查询当前登录用户的生成历史
    - image_url 懒回写
    - status 状态机（pending / success / failed）
    - 可选分页（不传参数时不分页）
    """

    query = (
        db.query(History)
        .filter(History.user_id == current_user.id)
        .order_by(History.id.desc())
    )

    # =========================
    # 只有显式传入参数时才分页
    # =========================
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    records = query.all()

    # =========================
    # 懒回写 image_url + status
    # =========================
    for h in records:
        if h.status == "pending":
            try:
                result = call_result(h.task_id)

                if result and result.get("status") == "success":
                    images = result.get("images", [])
                    if images:
                        # -------------------------
                        # 原有成功终态逻辑
                        # -------------------------
                        h.image_url = images[0].get("url")
                        h.status = "success"

                        # =========================
                        # v1.0.30 · 荣誉系统
                        # 成功生成任务累积
                        # =========================
                        before_total = current_user.total_success_tasks
                        current_user.total_success_tasks += 1
                        after_total = current_user.total_success_tasks

                        # 计算 after 快照
                        snapshot_after = calculate_honor_levels(after_total)

                        current_user.level_star = snapshot_after.level_star
                        current_user.level_moon = snapshot_after.level_moon
                        current_user.level_sun = snapshot_after.level_sun
                        current_user.level_diamond = snapshot_after.level_diamond
                        current_user.level_crown = snapshot_after.level_crown

                        # =========================
                        # v1.0.30 · 强度晋级判定与奖励
                        # =========================
                        reward_quota = 0
                        if is_strength_upgrade(before_total, after_total):
                            reward_quota = random.randint(1, 3)

                            current_user.quota += reward_quota

                            quota_log = QuotaLog(
                                user_id=current_user.id,
                                change=reward_quota,
                                reason="honor_level_reward",
                                operator_id=None,
                            )
                            db.add(quota_log)

                        # =========================
                        # v1.0.30 · 等级事件记录
                        # =========================
                        snapshot_before = calculate_honor_levels(before_total)

                        db.execute(
                            """
                            INSERT INTO honor_level_events (
                                user_id,
                                trigger,
                                before_total_success_tasks,
                                after_total_success_tasks,
                                before_star, after_star,
                                before_moon, after_moon,
                                before_sun, after_sun,
                                before_diamond, after_diamond,
                                before_crown, after_crown,
                                reward_quota_delta
                            ) VALUES (
                                :user_id,
                                :trigger,
                                :before_total, :after_total,
                                :before_star, :after_star,
                                :before_moon, :after_moon,
                                :before_sun, :after_sun,
                                :before_diamond, :after_diamond,
                                :before_crown, :after_crown,
                                :reward_quota
                            )
                            """,
                            {
                                "user_id": current_user.id,
                                "trigger": "LEVEL_UP"
                                if reward_quota > 0
                                else "SUCCESS_TASK_INCREMENT",
                                "before_total": before_total,
                                "after_total": after_total,
                                "before_star": snapshot_before.level_star,
                                "after_star": snapshot_after.level_star,
                                "before_moon": snapshot_before.level_moon,
                                "after_moon": snapshot_after.level_moon,
                                "before_sun": snapshot_before.level_sun,
                                "after_sun": snapshot_after.level_sun,
                                "before_diamond": snapshot_before.level_diamond,
                                "after_diamond": snapshot_after.level_diamond,
                                "before_crown": snapshot_before.level_crown,
                                "after_crown": snapshot_after.level_crown,
                                "reward_quota": reward_quota,
                            },
                        )

                        db.add(current_user)
                        db.add(h)
                        db.commit()

                elif result and result.get("status") == "failed":
                    h.status = "failed"
                    db.add(h)
                    db.commit()

            except Exception:
                # 任何异常都不影响列表返回
                pass

    # =========================
    # v1.0.7 核心修复点
    # 不再手工拼 dict
    # =========================
    return records
