import os
import time
import threading
import logging
import requests

# ===== 基础配置（只读，不强依赖） =====
# 支持多个后端端点
PLATFORM_EVENT_ENDPOINT = os.getenv(
    "PLATFORM_EVENT_ENDPOINT",
    ""
)

COMPUTE_NODE = os.getenv(
    "COMPUTE_NODE",
    "unknown"
)

# ===== 内存级最小事实缓存 =====
# 仅用于本进程生命周期内的事实对账，不做裁决

_event_cache = {}
_event_lock = threading.Lock()


def emit_event(prompt_id: str, phase: str, payload: dict | None = None):
    """
    上报事实事件：
    - 绝不抛异常
    - 绝不阻塞主线程
    - 失败即吞
    """
    
    event = {
        "source": "comfyui",
        "compute_node": COMPUTE_NODE,
        "prompt_id": prompt_id,
        "phase": phase,
        "timestamp": int(time.time() * 1000),
        "payload": payload or {},
    }

    # 本地事实缓存（仅记录最后一次）
    try:
        with _event_lock:
            _event_cache[prompt_id] = event
    except Exception:
        pass

    # 未配置平台端点则只记本地事实
    if not PLATFORM_EVENT_ENDPOINT:
        logging.info(f"[event] {event}")
        return

    # 后台线程发送，避免阻塞
    def _post():
        try:
            requests.post(
                PLATFORM_EVENT_ENDPOINT,
                json=event,
                timeout=1.5,
            )
        except Exception:
            pass

    try:
        threading.Thread(target=_post, daemon=True).start()
    except Exception:
        pass


def get_cached_event(prompt_id: str):
    with _event_lock:
        return _event_cache.get(prompt_id)
