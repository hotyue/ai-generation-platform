from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.plan import Plan
from backend.app.schemas.plan import PlanUpdate
from backend.app.models.quota_log import QuotaLog
from backend.app.routers.auth import get_current_user
from backend.app.utils.user_events import emit_user_quota_event
from backend.app.ws.events import emit_account_status_event  # v1.0.11

router = APIRouter(prefix="/admin", tags=["Admin"])


# =========================
# 权限校验
# =========================
def require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="管理员权限不足")


# =========================
# 请求模型
# =========================
class GrantQuotaRequest(BaseModel):
    quota: int
    reason: str | None = "manual_grant"


# =========================
# 1️⃣ 管理员人工充值 quota
# =========================
@router.post("/users/{user_id}/grant")
def grant_quota(
    user_id: int,
    req: GrantQuotaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    if req.quota <= 0:
        raise HTTPException(status_code=400, detail="充值额度必须大于 0")

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.quota += req.quota
    db.add(user)

    quota_log = QuotaLog(
        user_id=user.id,
        change=req.quota,
        reason=req.reason or "manual_grant",
        operator_id=current_user.id,
    )
    db.add(quota_log)

    db.commit()
    db.refresh(user)

    try:
        emit_user_quota_event(
            user_id=user.id,
            balance=user.quota,
        )
    except Exception:
        pass

    return {
        "msg": "充值成功",
        "user_id": user.id,
        "quota_added": req.quota,
        "quota_now": user.quota,
        "reason": req.reason,
    }


# =========================
# 2️⃣ 管理员给用户绑定套餐
# =========================
@router.post("/users/{user_id}/apply-plan/{plan_id}")
def apply_plan(
    user_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.is_active == True,
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在或已停用")

    user.quota += plan.quota
    db.add(user)

    quota_log = QuotaLog(
        user_id=user.id,
        change=plan.quota,
        reason=f"plan:{plan.name}",
        operator_id=current_user.id,
    )
    db.add(quota_log)

    db.commit()
    db.refresh(user)

    try:
        emit_user_quota_event(
            user_id=user.id,
            balance=user.quota,
        )
    except Exception:
        pass

    return {
        "msg": "套餐已应用",
        "user_id": user.id,
        "plan": {
            "id": plan.id,
            "name": plan.name,
            "quota": plan.quota,
        },
        "quota_now": user.quota,
    }


# =========================
# 3️⃣ 管理员获取用户列表
# =========================
@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    users = db.query(User).filter(
        User.is_deleted == False
    ).order_by(User.id.desc()).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "quota": u.quota,
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]


# =========================
# 4️⃣ 管理员获取套餐列表
# =========================
@router.get("/plans")
def list_plans_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return db.query(Plan).order_by(Plan.id.desc()).all()


# =========================
# 5️⃣ 管理员创建套餐
# =========================
class CreatePlanRequest(BaseModel):
    name: str
    quota: int
    price: float = 0


@router.post("/plans")
def create_plan(
    req: CreatePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    if req.quota <= 0:
        raise HTTPException(status_code=400, detail="套餐额度必须大于 0")

    plan = Plan(
        name=req.name,
        quota=req.quota,
        price=req.price,
        is_active=True,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {"msg": "套餐创建成功", "plan": plan}


# =========================
# 6️⃣ 管理员修改套餐
# =========================
@router.put("/plans/{plan_id}")
def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")

    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="未提供任何可修改字段")

    for field, value in update_data.items():
        setattr(plan, field, value)

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {"msg": "套餐修改成功", "plan": plan}


# =========================
# 7️⃣ 管理员停用 / 启用套餐
# =========================
@router.post("/plans/{plan_id}/disable")
def disable_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")

    plan.is_active = False
    db.add(plan)
    db.commit()

    return {"msg": "套餐已停用", "plan_id": plan.id}


@router.post("/plans/{plan_id}/enable")
def enable_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")

    plan.is_active = True
    db.add(plan)
    db.commit()

    return {"msg": "套餐已启用", "plan_id": plan.id}


# =========================
# 账号状态治理（v1.0.11 · 正确版）
# =========================
@router.post("/users/{user_id}/restrict")
async def restrict_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.account_status != "normal":
        raise HTTPException(status_code=409, detail="当前状态不可设为受限")

    user.account_status = "restricted"
    db.add(user)
    db.commit()
    db.refresh(user)

    await emit_account_status_event(
        user_id=user.id,
        account_status=user.account_status,
    )

    return {
        "msg": "用户已设为受限",
        "user_id": user.id,
        "account_status": user.account_status,
    }


@router.post("/users/{user_id}/unrestrict")
async def unrestrict_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.account_status != "restricted":
        raise HTTPException(status_code=409, detail="当前状态不可解除受限")

    user.account_status = "normal"
    db.add(user)
    db.commit()
    db.refresh(user)

    await emit_account_status_event(
        user_id=user.id,
        account_status=user.account_status,
    )

    return {
        "msg": "用户受限状态已解除",
        "user_id": user.id,
        "account_status": user.account_status,
    }


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.account_status = "banned"
    db.add(user)
    db.commit()
    db.refresh(user)

    await emit_account_status_event(
        user_id=user.id,
        account_status=user.account_status,
    )

    return {
        "msg": "用户已封禁",
        "user_id": user.id,
        "account_status": user.account_status,
    }


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.account_status != "banned":
        raise HTTPException(status_code=409, detail="当前状态不可解封")

    user.account_status = "normal"
    db.add(user)
    db.commit()
    db.refresh(user)

    await emit_account_status_event(
        user_id=user.id,
        account_status=user.account_status,
    )

    return {
        "msg": "用户已解封",
        "user_id": user.id,
        "account_status": user.account_status,
    }
