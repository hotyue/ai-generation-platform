from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.history import History
from backend.app.models.user import User
from backend.app.routers.auth import get_current_user
from backend.app.schemas.history import HistoryItem
from backend.app.utils.http_client import call_result

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=List[HistoryItem],
)
def list_history(
    limit: int | None = Query(default=None, ge=1, le=100),
    offset: int | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    v1.0.30 · 历史查询接口（只读）

    - 查询历史记录
    - 允许 image_url 懒回填（不推进状态）
    - 不写 success / failed
    - 不推进荣誉系统
    """

    query = (
        db.query(History)
        .filter(History.user_id == current_user.id)
        .order_by(History.id.desc())
    )

    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    records = query.all()

    # =========================
    # 懒回填 image_url（仅展示优化）
    # ⚠️ 不写 status，不 commit
    # =========================
    for h in records:
        if h.status == "pending" and not h.image_url:
            try:
                result = call_result(h.task_id)
                images = (result or {}).get("images", [])
                if images:
                    h.image_url = images[0].get("url")
                    db.add(h)
                    db.commit()
            except Exception:
                pass

    return records
