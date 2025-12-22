# backend/app/middlewares/account_status.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.utils.jwt_utils import decode_access_token


MethodPath = Tuple[str, str]


@dataclass(frozen=True)
class AccountStatusPolicy:
    allow_all: bool
    allow: Tuple[MethodPath, ...] = ()


# ============================================================
# v1.0.10 · account_status 行为矩阵（冻结级 · 唯一法律依据）
# ============================================================
ACCOUNT_STATUS_RULES = {
    "normal": AccountStatusPolicy(
        allow_all=True,
        allow=(),
    ),
    "restricted": AccountStatusPolicy(
        allow_all=False,
        allow=(
            ("GET", "/api/auth/me"),
            ("GET", "/api/history"),
            ("GET", "/api/plans"),
            ("GET", "/api/quota/logs"),
        ),
    ),
    "banned": AccountStatusPolicy(
        allow_all=False,
        allow=(),
    ),
}

# ============================================================
# 全局免登录路径（⚠️ 不允许出现 "/"）
# ============================================================
EXEMPT_PATH_PREFIXES: Tuple[str, ...] = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/login",
    "/api/auth/register",
    "/api/health",
    "/health",
)

# ============================================================
# account_status 豁免（按角色治理）
# ============================================================
EXEMPT_ACCOUNT_STATUS_PREFIXES: Tuple[str, ...] = (
    "/api/admin",
)


def _is_exempt_path(path: str) -> bool:
    # 根路径只允许精确匹配
    if path == "/":
        return True

    for p in EXEMPT_PATH_PREFIXES:
        if path == p or path.startswith(p + "/"):
            return True
    return False


def _is_exempt_account_status(path: str) -> bool:
    for p in EXEMPT_ACCOUNT_STATUS_PREFIXES:
        if path == p or path.startswith(p + "/"):
            return True
    return False


def _extract_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    return token or None


def _is_allowed_strict(
    policy: AccountStatusPolicy,
    method: str,
    path: str,
) -> bool:
    if policy.allow_all:
        return True

    for allow_method, allow_path in policy.allow:
        if method != allow_method:
            continue
        if path == allow_path or path.startswith(allow_path + "/"):
            return True

    return False


class AccountStatusMiddleware(BaseHTTPMiddleware):
    """
    v1.0.10 · account_status 统一裁决中间件（最终冻结版）

    重要原则：
    - BaseHTTPMiddleware 中 **不得 raise HTTPException**
    - 必须 return Response（否则 Python 3.11 + anyio 会触发 ExceptionGroup → 500）
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method.upper()

        # 0️⃣ 非 API 请求不治理
        if not path.startswith("/api"):
            return await call_next(request)

        # 1️⃣ 免登录路径
        if _is_exempt_path(path):
            return await call_next(request)

        # 2️⃣ 必须登录
        token = _extract_bearer_token(request)
        if token is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "未登录或 Token 缺失"},
            )

        try:
            payload = decode_access_token(token)
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 无效或已过期"},
            )

        if not payload or "sub" not in payload:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 无效或已过期"},
            )

        try:
            user_id = int(payload["sub"])
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 无效"},
            )

        # 3️⃣ 查用户
        db = SessionLocal()
        try:
            user = (
                db.query(User)
                .filter(User.id == user_id, User.is_deleted == False)
                .first()
            )
        finally:
            db.close()

        if user is None or not user.is_active or user.is_deleted:
            return JSONResponse(
                status_code=401,
                content={"detail": "用户不存在或已被禁用"},
            )

        # 4️⃣ admin 接口：豁免 account_status
        if _is_exempt_account_status(path):
            return await call_next(request)

        # 5️⃣ account_status 严格裁决
        policy = ACCOUNT_STATUS_RULES.get((user.account_status or "normal").strip())
        if policy is None:
            return JSONResponse(
                status_code=403,
                content={"detail": "账号状态异常，已拒绝该操作"},
            )

        if not _is_allowed_strict(policy, method, path):
            return JSONResponse(
                status_code=403,
                content={"detail": "账号当前状态不可执行该操作"},
            )

        return await call_next(request)
