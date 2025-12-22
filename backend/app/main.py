import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import task, generate, history, auth, admin, plan, quota
from backend.app.middlewares.account_status import AccountStatusMiddleware  # ✅ v1.0.10 新增

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
# ✅ v1.0.10：account_status 统一中间件（全局兜底）
# ⚠️ 必须在 include_router 之前
# =========================
app.add_middleware(AccountStatusMiddleware)

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
