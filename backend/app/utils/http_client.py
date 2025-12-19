import requests
from urllib.parse import urlparse, urlunparse
from backend.app.config import COMFY_API_BASE


def _force_https(url: str) -> str:
    """
    强制将 http:// 转为 https://
    解决前端 Mixed Content 问题
    """
    if not url:
        return url

    parsed = urlparse(url)

    if parsed.scheme == "http":
        return urlunparse(parsed._replace(scheme="https"))

    return url


def call_generate(prompt: str):
    url = f"{COMFY_API_BASE}/generate"
    resp = requests.post(url, json={"prompt": prompt})
    resp.raise_for_status()
    return resp.json()


def call_result(task_id: str):
    url = f"{COMFY_API_BASE}/result/{task_id}"
    resp = requests.get(url)
    resp.raise_for_status()

    data = resp.json()

    # =========================
    # 🔑 关键修复：统一修正 image.url
    # =========================
    images = data.get("images", [])
    for img in images:
        if "url" in img:
            img["url"] = _force_https(img["url"])

    return data
