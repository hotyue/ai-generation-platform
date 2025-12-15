from fastapi import APIRouter, WebSocket, Depends
from app.ws.manager import manager
from app.routers.auth import get_current_user_ws  # 你已有 auth，可复用

router = APIRouter()

@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, user=Depends(get_current_user_ws)):
    await manager.connect(user.id, websocket)
    try:
        while True:
            # v1：只做下行广播，忽略客户端消息
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        manager.disconnect(user.id, websocket)
