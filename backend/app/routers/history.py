from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.history import History
from backend.app.models.user import User
from backend.app.routers.auth import get_current_user
from backend.app.schemas.history import HistoryItem
from backend.app.utils.http_client import call_result
from backend.app.utils.honor_level import calculate_honor_levels

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
    # （保留原有业务语义，不影响 v1.0.7）
    # =========================
    for h in records:
        if h.status == "pending":
            try:
                result = call_result(h.task_id)

                if result and result.get("status") == "success":
                    images = result.get("images", [])
                    if images:
                        h.image_url = images[0].get("url")
                        h.status = "success"
                        # v1.0.30 · 荣誉系统：成功生成任务累积
                        user.total_success_tasks += 1

                        snapshot = calculate_honor_levels(user.total_success_tasks)

                        user.level_star = snapshot.level_star
                        user.level_moon = snapshot.level_moon
                        user.level_sun = snapshot.level_sun
                        user.level_diamond = snapshot.level_diamond
                        user.level_crown = snapshot.level_crown

                        db.add(user)

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
    # ⚠️ v1.0.7 核心修复点
    # 不再手工拼 dict
    # 直接返回 ORM，由 response_model 触发 UTCModel
    # =========================
    return records
