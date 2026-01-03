from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.history import History
from backend.app.models.user import User
from backend.app.routers.auth import get_current_user
from backend.app.schemas.history import HistoryItem

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
    v1.0.31 · 历史查询接口（只读）

    - 查询用户历史记录
    - 不推进生成状态
    - 不进行任何事实回填
    - 返回的 image_url 为后端裁决后的最优展示URL
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
    # v1.0.31 · 历史展示 URL 选择
    # archive_url 优先，image_url 兜底
    # =========================
    for h in records:
        if h.archive_url:
            h.image_url = h.archive_url

    return records
