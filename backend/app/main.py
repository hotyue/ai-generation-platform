import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.routers import task, generate, history, auth, admin, plan, quota
from backend.app.middlewares.account_status import AccountStatusMiddleware  # v1.0.10

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
# ⚠️ 必须在 include_router 之前
# =========================
app.add_middleware(AccountStatusMiddleware)

# =========================
# ⭐ v1.0.10：account_status 统一 Response 出口
# ⭐ 目的：确保拒绝响应一定携带 CORS 头
# =========================
@app.middleware("http")
async def account_status_response_wrapper(request: Request, call_next):
    response = await call_next(request)

    denied = getattr(request.state, "account_status_denied", None)
    if denied:
        return JSONResponse(
            status_code=denied["status_code"],
            content={"detail": denied["detail"]},
            headers=response.headers,  # ⭐ 保留 CORS / credentials 等头
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

@app.get("/")
def root():
    return {"msg": "Backend is running"}
