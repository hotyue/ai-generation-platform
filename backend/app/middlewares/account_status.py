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

# ============================
# account_status 行为矩阵
# ============================
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

# ============================
# 免登录路径
# ============================
EXEMPT_PATH_PREFIXES: Tuple[str, ...] = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/login",
    "/api/auth/register",
    "/api/health",
    "/health",
)

# ============================
# account_status 豁免（按角色治理）
# ============================
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
    统一账号状态裁决中间件（修正版）

    主要逻辑：
    - 检查请求中是否携带有效 token
    - 根据用户的账号状态（正常、受限、封禁）进行权限控制
    - 封禁用户：拒绝访问所有 API，返回 403
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 0️⃣ 处理 CORS 预检请求
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        method = request.method.upper()

        # 1️⃣ 非 API 请求不处理
        if not path.startswith("/api"):
            return await call_next(request)

        # 2️⃣ 免登录路径放行
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

        # 4️⃣ 查找用户
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

        # 5️⃣ admin 接口：豁免 account_status 校验
        if _is_exempt_account_status(path):
            return await call_next(request)

        # ⭐ 特殊规则：auth/me 必须永远允许
        if method == "GET" and path == "/api/auth/me":
            return await call_next(request)

        # 6️⃣ 账户状态严格裁决
        policy = ACCOUNT_STATUS_RULES.get((user.account_status or "normal").strip())
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

        # 7️⃣ 封禁用户拒绝访问所有 API
        if user.account_status == "banned":
            request.state.account_status_denied = {
                "status_code": 403,
                "detail": "您的账号已被封禁，无法继续使用",
            }
            return await call_next(request)

        return await call_next(request)
