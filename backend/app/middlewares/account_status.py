from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

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
        allow=(
            # ⭐ 必须允许 auth/me
            ("GET", "/api/auth/me"),
        ),
    ),
}

# ============================================================
# 全局免登录路径（HTTP 语义）
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
# account_status 豁免（管理员接口）
# ============================================================
EXEMPT_ACCOUNT_STATUS_PREFIXES: Tuple[str, ...] = (
    "/api/admin",
)


def _is_exempt_path(path: str) -> bool:
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
    return auth.split(" ", 1)[1].strip() or None


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

    v1.0.21 补充约束：
    - WebSocket 请求不进入 account_status 裁决体系
    - WebSocket 的鉴权与状态治理由 WS 内部完成
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # ⭐ v1.0.21：WebSocket 请求直接放行（不参与 HTTP account_status 裁决）
        if request.scope.get("type") == "websocket":
            return await call_next(request)

        # 0️⃣ CORS 预检
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        method = request.method.upper()

        # 1️⃣ 非 API 请求
        if not path.startswith("/api"):
            return await call_next(request)

        # 2️⃣ 免登录路径
        if _is_exempt_path(path):
            return await call_next(request)

        # 3️⃣ 必须登录
        token = _extract_bearer_token(request)
        if token is None:
            request.state.account_status_denied = {
                "status_code": 401,
                "detail": "未登录或 Token 缺失",
            }
            return await call_next(request)

        try:
            payload = decode_access_token(token)
        except Exception:
            request.state.account_status_denied = {
                "status_code": 401,
                "detail": "Token 无效或已过期",
            }
            return await call_next(request)

        if not payload or "sub" not in payload:
            request.state.account_status_denied = {
                "status_code": 401,
                "detail": "Token 无效或已过期",
            }
            return await call_next(request)

        try:
            user_id = int(payload["sub"])
        except Exception:
            request.state.account_status_denied = {
                "status_code": 401,
                "detail": "Token 无效",
            }
            return await call_next(request)

        # 4️⃣ 查询用户
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
            request.state.account_status_denied = {
                "status_code": 401,
                "detail": "用户不存在或已被禁用",
            }
            return await call_next(request)

        # 5️⃣ 管理员接口豁免
        if _is_exempt_account_status(path):
            return await call_next(request)

        # 6️⃣ account_status 裁决（HTTP 唯一入口）
        status_key = (user.account_status or "normal").strip()
        policy = ACCOUNT_STATUS_RULES.get(status_key)

        if policy is None:
            request.state.account_status_denied = {
                "status_code": 403,
                "detail": "账号状态异常，已拒绝该操作",
            }
            return await call_next(request)

        if not _is_allowed_strict(policy, method, path):
            request.state.account_status_denied = {
                "status_code": 403,
                "detail": "账号当前状态不可执行该操作",
            }
            return await call_next(request)

        return await call_next(request)
