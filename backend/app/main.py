import os
import threading
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.routers import task, generate, history, auth, admin, plan, quota, ws
from backend.app.middlewares.account_status import AccountStatusMiddleware  # v1.0.10

# =========================
# v1.0.30 · 后台事实推进器
# =========================
# ✅ 与 services/history_facts_advancer.py 中真实函数名保持一致
from backend.app.services.history_facts_advancer import (
    history_facts_advancer_loop,
)

# =========================
# v1.0.30 · 荣誉事实推进器
# =========================
from backend.app.services.honor_facts_advancer import (
    honor_facts_advancer_loop,
)

logger = logging.getLogger("startup")

# =========================
# 1️⃣ 创建 FastAPI 应用
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
app.include_router(ws.router)

# =========================
# 🌟 v1.0.30 · 启动后台事实推进器
# =========================
@app.on_event("startup")
def start_history_facts_advancer():
    """
    v1.0.30
    后台生成事实推进器：
    - 周期性扫描 histories.status = pending
    - 推进 success / failed 事实
    """

    enabled = os.getenv("HISTORY_FACTS_ADVANCER_ENABLED", "1") == "1"
    if not enabled:
        logger.warning(
            "[startup] history facts advancer disabled by env"
        )
        return

    t = threading.Thread(
        target=history_facts_advancer_loop,
        name="history-facts-advancer",
        daemon=True,
    )
    t.start()

    logger.info(
        "[startup] history facts advancer thread started"
    )
# =========================
# 🌟 v1.0.30 · 启动荣誉事实推进器
# =========================
@app.on_event("startup")
def start_honor_facts_advancer():
    """
    v1.0.30
    后台荣誉事实推进器：
    - 扫描成功生成历史
    - 推进荣誉等级与奖励事实
    - 提交成功后发送 WS 通知
    """

    enabled = os.getenv("HONOR_FACTS_ADVANCER_ENABLED", "1") == "1"
    if not enabled:
        logger.warning(
            "[startup] honor facts advancer disabled by env"
        )
        return

    t = threading.Thread(
        target=honor_facts_advancer_loop,
        name="honor-facts-advancer",
        daemon=True,
    )
    t.start()

    logger.info(
        "[startup] honor facts advancer thread started"
    )

@app.get("/")
def root():
    return {"msg": "Backend is running"}


# ======================================================
# 2️⃣ v1.0.28：API Canonical Path（⚠️关键修正点）
# ======================================================
# ❗ 必须在文件末尾用 ASGI 外层包裹
from backend.app.middlewares.api_canonical_path import APICanonicalPathMiddleware

app = APICanonicalPathMiddleware(app)
