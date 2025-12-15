from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.history import History
from app.models.user import User
from app.routers.auth import get_current_user
# call_result 保留导入（v1.0.2 / 后台任务会用到）
from app.utils.http_client import call_result

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/")
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
    - v1.0.1 方案 A：history 接口不阻塞等待生成结果
    - status 状态只读（pending / success / failed）
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

    results = []

    for h in records:
        image_url = h.image_url

        # =========================
        # v1.0.1 · 方案 A
        #
        # history 接口职责收敛为：
        # - 仅返回已知事实
        # - 不主动查询生成结果
        # - 不阻塞 / 不等待 / 不推进状态
        #
        # pending 状态：
        # - 直接原样返回
        # =========================
        if h.status == "pending":
            pass

        results.append({
            "id": h.id,
            "task_id": h.task_id,
            "prompt": h.prompt,
            "image_url": image_url,
            "status": h.status,
            "created_at": h.created_at,
        })

    # =========================
    # 返回结构：完全兼容旧版
    # =========================
    return results
