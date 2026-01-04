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

# ✅ 新增：事实事件上报（旁路，不影响主逻辑）
from app.services.comfy_event_reporter import emit_event


# -----------------------------------------
# 初始化 FastAPI
# -----------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------
# 配置区域（v1.0.31 冻结裁决）
# -----------------------------------------

# ComfyUI API（必须由环境变量提供）
COMFY_API = os.getenv("COMFY_API")
if not COMFY_API:
    raise RuntimeError("COMFY_API is required")

# 输出目录（Docker / 宿主统一语义）
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/data/outputs")

# image_url 统一由环境变量决定（语义冻结）
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
if not PUBLIC_BASE_URL:
    raise RuntimeError("PUBLIC_BASE_URL is required")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------
# 静态文件服务
# -----------------------------------------

# ⚠️ 说明：
# Docker + Nginx 场景下，/outputs 实际由 nginx 提供
# 这里保留 mount 仅用于：
# 1) Windows 直跑
# 2) 调试兜底
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# web：仅在 Windows 本地调试存在
WEB_DIR = os.getenv("WEB_DIR", "")
if WEB_DIR and os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


# -----------------------------------------
# 加载 workflow.json
# -----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_PATH = os.path.join(BASE_DIR, "workflows", "workflow.json")

with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
    WORKFLOW = json.load(f)

PROMPT_NODE_ID = "45"
SAVE_NODE_ID = "9"


# -----------------------------------------
# 请求模型
# -----------------------------------------
class PromptRequest(BaseModel):
    prompt: str


# -----------------------------------------
# 构建 workflow
# -----------------------------------------
def build_workflow(prompt: str, prompt_id: str):
    wf = copy.deepcopy(WORKFLOW)
    wf[PROMPT_NODE_ID]["inputs"]["text"] = prompt
    wf[SAVE_NODE_ID]["inputs"]["filename_prefix"] = prompt_id
    return wf


# -----------------------------------------
# 提交任务到 ComfyUI
# -----------------------------------------
def queue_prompt(wf):
    payload = {
        "prompt": wf,
        "client_id": str(uuid.uuid4())
    }

    resp = requests.post(f"{COMFY_API}/prompt", json=payload, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"提交任务失败 {resp.status_code}: {resp.text}")

    return resp.json().get("prompt_id")


# -----------------------------------------
# 查找输出文件
# -----------------------------------------
def find_output_files(prompt_id: str):
    pattern = os.path.join(OUTPUT_DIR, f"{prompt_id}*.png")
    return glob.glob(pattern)


# -----------------------------------------
# Cloudflare R2 异步上传
# -----------------------------------------
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


# -----------------------------------------
# 下发任务
# -----------------------------------------
@app.post("/generate")
def generate(req: PromptRequest):
    try:
        business_id = str(uuid.uuid4())
        wf = build_workflow(req.prompt, business_id)
        queue_prompt(wf)

        # ✅ 事实事件：任务已入队（queued）
        emit_event(prompt_id=business_id, phase="queued")

        return {
            "msg": "任务已提交",
            "prompt_id": business_id
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )


# -----------------------------------------
# 查询结果（平台轮询）
# -----------------------------------------
@app.get("/result/{prompt_id}")
def get_result(prompt_id: str, b64: int = 0):

    files = find_output_files(prompt_id)

    if files:
        results = []

        for fp in files:
            filename = os.path.basename(fp)

            # image_url（语义冻结）
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

        # ✅ 事实事件：任务已完成（finished）
        emit_event(prompt_id=prompt_id, phase="finished")

        return {
            "status": "success",
            "prompt_id": prompt_id,
            "images": results
        }

    # ---------------------------------
    # pending（保持原语义）
    # ---------------------------------
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
