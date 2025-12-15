from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.history import History
from app.models.user import User
from app.models.quota_log import QuotaLog
from app.routers.auth import get_current_user
from app.utils.http_client import call_generate
from app.utils.user_events import emit_user_quota_event

router = APIRouter(prefix="/generate", tags=["Generate"])


class GenerateRequest(BaseModel):
    prompt: str

@router.post("")
def generate_for_user(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ quota 校验（最终仍由后端兜底）
    if current_user.quota <= 0:
        raise HTTPException(status_code=400, detail="生成次数不足，请充值")

    # 2️⃣ 先创建 history（pending）
    # 说明：此处一旦 commit，pending 状态即成为系统事实
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

    # 5️⃣ 提交 DB 事务（钱与 pending 事实先成立）
    db.commit()
    db.refresh(current_user)
    db.refresh(history)

    # ================================
    # 6️⃣–7️⃣ 外部生成调用 + task_id 回填
    # 【修改点开始】
    # 目标：
    # - 任何异常都必须显式将 history 从 pending 推进到 failed
    # - 不引入重试、不做补偿，仅记录失败事实
    # ================================
    try:
        # 6️⃣ 调用 ComfyUI（外部系统）
        result = call_generate(req.prompt)

        # 外部系统返回不符合预期，视为生成失败
        if not result or "prompt_id" not in result:
            raise Exception("generate submit failed")

        # 7️⃣ 回填 task_id
        history.task_id = result["prompt_id"]
        db.add(history)
        db.commit()
        db.refresh(history)

    except Exception:
        # 【关键兜底逻辑】
        # 说明：
        # - 进入此分支意味着 generate 生命周期已结束
        # - 若不写回 failed，将导致 history 永久停留在 pending
        history.status = "failed"
        db.add(history)
        db.commit()
        db.refresh(history)

        # 对外仍返回 500，不泄露内部异常细节
        raise HTTPException(status_code=500, detail="生成任务提交失败")
    # 【修改点结束】

    # 8️⃣ 额度变更事件通知（非关键链路）
    try:
        emit_user_quota_event(
            user_id=current_user.id,
            balance=current_user.quota
        )
    except Exception:
        # 事件失败不影响 generate 主流程
        pass

    return {
        "msg": "Task submitted",
        "task_id": history.task_id,
        "quota_left": current_user.quota,
    }
