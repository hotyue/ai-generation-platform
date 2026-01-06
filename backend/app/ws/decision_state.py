"""
WS 裁决状态快照（v1.0.32）

仅保存最新一次裁决结果：
- X
- Y
- Z
"""

from typing import Dict, Optional
from threading import Lock

_lock = Lock()
_current_decision: Optional[Dict[str, float]] = None


def get_current_decision() -> Optional[Dict[str, float]]:
    with _lock:
        return dict(_current_decision) if _current_decision else None


def update_current_decision(decision: Dict[str, float]) -> bool:
    """
    更新裁决快照
    :return: 是否发生变化
    """
    global _current_decision
    with _lock:
        if _current_decision == decision:
            return False
        _current_decision = dict(decision)
        return True
