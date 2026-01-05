from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import requests
import uuid
import json
import base64
import os
import glob
import copy
import threading
from datetime import datetime

# ⚠️ 注意：保持原有导入方式不变
from app.services.archive import upload_to_r2

# ✅ 原有：事实事件上报（compute-api → 平台）
from app.services.comfy_event_reporter import emit_event


# =====================================================
# 初始化 FastAPI
# =====================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 配置区域（v1.0.31 冻结裁决）
# =====================================================

COMFY_API = os.getenv("COMFY_API")
if not COMFY_API:
    raise RuntimeError("COMFY_API is required")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/data/outputs")

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
if not PUBLIC_BASE_URL:
    raise RuntimeError("PUBLIC_BASE_URL is required")

PLATFORM_EVENT_ENDPOINT = os.getenv("PLATFORM_EVENT_ENDPOINT", "")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# 静态文件服务
# =====================================================
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

WEB_DIR = os.getenv("WEB_DIR", "")
if WEB_DIR and os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

# =====================================================
# ComfyUI → compute-api → 平台（只接、只转）
# =====================================================
@app.post("/internal/comfy/event")
async def recv_comfy_event(event: dict):
    """
    接收来自 ComfyUI 的事实事件（queued / running / finished）

    原则：
    - 不改内容
    - 不写库
    - 不裁决
    - 不影响原逻辑
    """
    if not PLATFORM_EVENT_ENDPOINT:
        return {"ok": True}

    try:
        requests.post(
            PLATFORM_EVENT_ENDPOINT,
            json=event,
            timeout=2,
        )
    except Exception:
        pass

    return {"ok": True}

# =====================================================
# 加载 workflow.json
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_PATH = os.path.join(BASE_DIR, "workflows", "workflow.json")

with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
    WORKFLOW = json.load(f)

PROMPT_NODE_ID = "45"
SAVE_NODE_ID = "9"

# =====================================================
# 请求模型
# =====================================================
class PromptRequest(BaseModel):
    prompt: str
    task_id: str | None = None  # ✅ 平台传入则用；不传则兼容旧行为

# =====================================================
# 构建 workflow
# =====================================================
def build_workflow(prompt: str, prompt_id: str):
    wf = copy.deepcopy(WORKFLOW)
    wf[PROMPT_NODE_ID]["inputs"]["text"] = prompt
    wf[SAVE_NODE_ID]["inputs"]["filename_prefix"] = prompt_id
    return wf

# =====================================================
# 提交任务到 ComfyUI（返回 comfy_prompt_id）
# =====================================================
def queue_prompt(wf):
    payload = {
        "prompt": wf,
        "client_id": str(uuid.uuid4())
    }

    resp = requests.post(f"{COMFY_API}/prompt", json=payload, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"提交任务失败 {resp.status_code}: {resp.text}")

    comfy_prompt_id = resp.json().get("prompt_id")
    if not comfy_prompt_id:
        raise RuntimeError("ComfyUI 未返回 prompt_id")

    return comfy_prompt_id

# =====================================================
# 查找输出文件
# =====================================================
def find_output_files(prompt_id: str):
    pattern = os.path.join(OUTPUT_DIR, f"{prompt_id}*.png")
    return glob.glob(pattern)

# =====================================================
# Cloudflare R2 异步上传
# =====================================================
def async_upload_to_r2(fp: str, filename: str):
    today = datetime.utcnow()
    object_key = (
        f"archive/"
        f"{today.year:04d}/"
        f"{today.month:02d}/"
        f"{today.day:02d}/"
        f"{filename}"
    )
    upload_to_r2(fp, object_key)

# =====================================================
# 下发任务（关键改造点）
# =====================================================
@app.post("/generate")
def generate(req: PromptRequest):
    try:
        # 平台业务主键（task_id）
        task_id = req.task_id
        if not task_id or task_id == "string":
            task_id = str(uuid.uuid4())

        # workflow 文件名仍使用 task_id（不破坏既有逻辑）
        wf = build_workflow(req.prompt, task_id)

        # 同步拿到 ComfyUI prompt_id
        comfy_prompt_id = queue_prompt(wf)

        # ===============================
        # ✅ 事实事件 1：身份绑定（新增）
        # ===============================
        emit_event(
            prompt_id=comfy_prompt_id,
            phase="bind",
            payload={
                "task_id": task_id
            }
        )

        # ===============================
        # ✅ 事实事件 2：平台视角 queued
        # ===============================
        emit_event(
            prompt_id=comfy_prompt_id,
            phase="queued",
            payload={
                "task_id": task_id
            }
        )

        return {
            "msg": "任务已提交",
            "task_id": task_id,
            "comfy_prompt_id": comfy_prompt_id
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# =====================================================
# 查询结果（平台轮询，完全不改）
# =====================================================
@app.get("/result/{prompt_id}")
def get_result(prompt_id: str, b64: int = 0):

    files = find_output_files(prompt_id)

    if files:
        results = []

        for fp in files:
            filename = os.path.basename(fp)

            url = f"{PUBLIC_BASE_URL}/{filename}"

            today = datetime.utcnow()
            object_key = (
                f"archive/"
                f"{today.year:04d}/"
                f"{today.month:02d}/"
                f"{today.day:02d}/"
                f"{filename}"
            )

            archive_url = upload_to_r2(fp, object_key)

            item = {
                "filename": filename,
                "url": url,
                "local_path": fp,
                "archive_url": archive_url,
                "archive_status": "success" if archive_url else "failed",
                "archive_error": None if archive_url else "upload_failed",
            }

            if b64 == 1:
                with open(fp, "rb") as f:
                    item["base64"] = base64.b64encode(f.read()).decode()

            threading.Thread(
                target=async_upload_to_r2,
                args=(fp, filename),
                daemon=True
            ).start()

            results.append(item)

        # ✅ 保留：完成事件
        emit_event(prompt_id=prompt_id, phase="finished")

        return {
            "status": "success",
            "prompt_id": prompt_id,
            "images": results
        }

    # pending（原样保留）
    try:
        hist_resp = requests.get(f"{COMFY_API}/history/{prompt_id}", timeout=5)
    except Exception:
        return {"status": "pending", "msg": "任务未开始或不存在"}

    if hist_resp.status_code != 200:
        return {"status": "pending", "msg": "任务未完成或不存在"}

    try:
        hist_json = hist_resp.json()
    except Exception:
        return {"status": "pending", "msg": "任务正在执行"}

    if not hist_json:
        return {"status": "pending", "msg": "任务正在执行"}

    return {"status": "pending", "msg": "任务正在执行"}
