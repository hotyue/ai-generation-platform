import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.routers import task, generate, history, auth, admin, plan, quota, ws
from backend.app.middlewares.account_status import AccountStatusMiddleware  # v1.0.10

# =========================
# 1️⃣ 创建 FastAPI 应用（原样）
# =========================
app = FastAPI(title="AI Generation Platform Backend")

# =========================
# ✅ CORS：由部署时注入前端来源（多客户交付）
# =========================
frontend_origins = os.getenv("FRONTEND_ORIGINS", "")

allow_origins = [
    origin.strip()
    for origin in frontend_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ✅ v1.0.10：account_status 统一中间件
# =========================
app.add_middleware(AccountStatusMiddleware)

# =========================
# ⭐ v1.0.10：account_status 统一 Response 出口
# =========================
@app.middleware("http")
async def account_status_response_wrapper(request: Request, call_next):
    response = await call_next(request)

    denied = getattr(request.state, "account_status_denied", None)
    if denied:
        return JSONResponse(
            status_code=denied["status_code"],
            content={"detail": denied["detail"]},
            headers=response.headers,
        )

    return response

# =========================
# ✅ 统一 API 前缀
# =========================
API_PREFIX = "/api"

app.include_router(task.router, prefix=API_PREFIX)
app.include_router(generate.router, prefix=API_PREFIX)
app.include_router(history.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(plan.router, prefix=API_PREFIX)
app.include_router(quota.router, prefix=API_PREFIX)

# =========================
# ✅ WebSocket 路由
# =========================
# v1.0.23 冷停验证：
# 历史 /ws/account-status WebSocket 入口不再注册进运行态
# （保留代码，不删除、不退役，仅断开路由）
# app.include_router(account_status.router)

app.include_router(ws.router)


@app.get("/")
def root():
    return {"msg": "Backend is running"}


# ======================================================
# 2️⃣ v1.0.28：API Canonical Path（⚠️关键修正点）
# ======================================================
# ❗ 不能使用 app.add_middleware
# ❗ 必须在“文件末尾”用 ASGI 外层包裹
from backend.app.middlewares.api_canonical_path import APICanonicalPathMiddleware

app = APICanonicalPathMiddleware(app)
