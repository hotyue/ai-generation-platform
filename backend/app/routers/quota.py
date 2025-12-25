# app/routers/quota.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.quota_log import QuotaLog
from backend.app.models.user import User
from backend.app.routers.auth import get_current_user

from datetime import datetime, timezone

router = APIRouter(prefix="/quota", tags=["Quota"])

@router.get("/logs")
def list_quota_logs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = (
        db.query(QuotaLog)
        .filter(QuotaLog.user_id == current_user.id)
        .order_by(QuotaLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "change": log.change,
            "reason": log.reason,
            "related_plan_id": log.related_plan_id,
            "operator_id": log.operator_id,
#            "created_at": log.created_at,
            "created_at": log.created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        for log in logs
    ]
