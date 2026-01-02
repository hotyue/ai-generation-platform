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
# 配置区域
# -----------------------------------------

COMFY_API = "http://127.0.0.1:8188"

OUTPUT_DIR = "D:/ComfyUI_windows_portable/ComfyUI/output"

# image_url（即时访问，原语义不变）
PUBLIC_BASE_URL = "https://aiimg.598000.xyz/outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 静态文件服务（原样保留）
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/web", StaticFiles(directory="D:/AI-Web/web"), name="web")

# 加载 workflow.json
with open("workflow.json", "r", encoding="utf-8") as f:
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

    resp = requests.post(f"{COMFY_API}/prompt", json=payload)
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
# Cloudflare R2 异步上传（原逻辑保留）
# -----------------------------------------
def async_upload_to_r2(fp: str, filename: str):
    """
    archive 路径规则（冻结）：
    archive/yyyy/mm/dd/filename
    """
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
            url = f"{PUBLIC_BASE_URL}/{filename}"

            # -----------------------------
            # v1.0.31 扩展：archive 裁决
            # -----------------------------
            today = datetime.utcnow()
            object_key = (
                f"archive/"
                f"{today.year:04d}/"
                f"{today.month:02d}/"
                f"{today.day:02d}/"
                f"{filename}"
            )

            archive_url = upload_to_r2(fp, object_key)

            if archive_url:
                archive_status = "success"
                archive_error = None
            else:
                archive_status = "failed"
                archive_error = "upload_failed"

            # -----------------------------
            # 原有异步行为保留（不阻塞）
            # -----------------------------
            threading.Thread(
                target=async_upload_to_r2,
                args=(fp, filename),
                daemon=True
            ).start()

            # -----------------------------
            # 结果项（原字段全部保留）
            # -----------------------------
            item = {
                # 原有字段（完全不动）
                "filename": filename,
                "url": url,
                "local_path": fp,

                # v1.0.31 新增字段（兼容扩展）
                "archive_url": archive_url,
                "archive_status": archive_status,
                "archive_error": archive_error,
            }

            if b64 == 1:
                with open(fp, "rb") as f:
                    item["base64"] = base64.b64encode(f.read()).decode()

            results.append(item)

        return {
            "status": "success",
            "prompt_id": prompt_id,
            "images": results
        }

    # ---------------------------------
    # 未生成 → pending（原逻辑不变）
    # ---------------------------------
    try:
        hist_resp = requests.get(f"{COMFY_API}/history/{prompt_id}")
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
