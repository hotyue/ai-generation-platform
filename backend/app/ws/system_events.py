def build_system_ws_event(event_type: str) -> dict:
    """
    v1.0.18 Phase 2.3
    构建 system-level WS 事件（治理级）
    """
    return {
        "event_type": event_type,
        "payload": {},
    }
