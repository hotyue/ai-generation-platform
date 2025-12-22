from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.history import History
from backend.app.models.user import User
from backend.app.models.quota_log import QuotaLog
from backend.app.routers.auth import get_current_user
from backend.app.utils.http_client import call_generate
from backend.app.utils.user_events import emit_user_quota_event

router = APIRouter(prefix="/generate", tags=["Generate"])


class GenerateRequest(BaseModel):
    prompt: str


@router.post("")
def generate_for_user(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ⚠️ v1.0.10 起：
    # account_status 裁决已统一迁移至 AccountStatusMiddleware
    # 此处不再做任何 account_status 判断

    # 1️⃣ quota 校验
    if current_user.quota <= 0:
        raise HTTPException(status_code=400, detail="生成次数不足，请充值")

    # 2️⃣ 先创建 history（pending）
    history = History(
        user_id=current_user.id,
        task_id=None,
        prompt=req.prompt,
        image_url=None,
        status="pending",
    )
    db.add(history)

    # 3️⃣ 扣减 quota
    current_user.quota -= 1
    db.add(current_user)

    # 4️⃣ quota 流水
    quota_log = QuotaLog(
        user_id=current_user.id,
        change=-1,
        reason="generate",
        operator_id=None,
    )
    db.add(quota_log)

    # 5️⃣ 提交 DB 事务（钱与事实先成立）
    db.commit()
    db.refresh(current_user)
    db.refresh(history)

    # 6️⃣ 调用 ComfyUI（外部系统）
    result = call_generate(req.prompt)
    if not result or "prompt_id" not in result:
        # v1：不回滚 quota，只记录失败（后续补偿）
        history.status = "failed"
        db.add(history)
        db.commit()
        db.refresh(history)
        raise HTTPException(status_code=500, detail="生成任务提交失败")

    # 7️⃣ 回填 task_id
    history.task_id = result["prompt_id"]
    db.add(history)
    db.commit()
    db.refresh(history)

    try:
        emit_user_quota_event(
            user_id=current_user.id,
            balance=current_user.quota
        )
    except Exception:
        pass

    return {
        "msg": "Task submitted",
        "task_id": history.task_id,
        "quota_left": current_user.quota,
    }
