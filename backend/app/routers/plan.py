from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.plan import Plan

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("")
def list_plans(
    db: Session = Depends(get_db),
):
    """
    F2 / G4 使用：
    - 套餐列表只读接口（普通用户）
    - ✅ 仅返回「可用套餐」
    - ❌ 不返回已停用套餐
    - 不涉及购买、不涉及 quota 变更
    """

    plans = (
        db.query(Plan)
        .filter(Plan.is_active == True)   # ⭐ 核心修复点
        .order_by(Plan.id.asc())
        .all()
    )

    return [
        {
            "id": p.id,
            "name": p.name,
            "quota": p.quota,
            "price": p.price,
            "is_active": p.is_active,
        }
        for p in plans
    ]
