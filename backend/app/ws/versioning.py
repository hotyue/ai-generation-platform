from fastapi import WebSocket


def extract_ws_protocol_version(websocket: WebSocket) -> int:
    """
    v1.0.18 Phase 2.1
    提取 WS 协议 version（治理级，不影响业务）

    优先级：
    1. Sec-WebSocket-Protocol
    2. Query 参数 ?v=
    3. 默认 0（等价 v1.0.17）
    """

    # 1️⃣ Sec-WebSocket-Protocol（如：aiweb.v1）
    protocol = websocket.headers.get("sec-websocket-protocol")
    if protocol:
        # 允许格式：v1 / aiweb.v1 / 1
        for part in protocol.split(","):
            part = part.strip()
            if part.endswith(".v1") or part == "v1" or part == "1":
                return 1

    # 2️⃣ Query 参数 ?v=
    v = websocket.query_params.get("v")
    if v == "1":
        return 1

    # 3️⃣ 默认
    return 0
