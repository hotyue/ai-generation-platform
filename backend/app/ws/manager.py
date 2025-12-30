from typing import Dict, Set, Optional
from fastapi import WebSocket
import asyncio
import logging
import threading
import concurrent.futures

logger = logging.getLogger("ws-manager")


class ConnectionManager:
    def __init__(self):
        # user_id -> set(WebSocket)
        self._users: Dict[int, Set[WebSocket]] = {}

        # 关键：捕获并固化“运行中的事件循环”
        # - connect() 一定发生在 uvicorn 的事件循环中
        # - 一旦捕获到 loop，后台线程可用 run_coroutine_threadsafe 投递发送任务
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_lock = threading.Lock()

    def _ensure_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """
        尽力获取/刷新事件循环引用。
        只在“有运行循环”的上下文中调用（例如 connect / send_to_user async）。
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return self._loop

        with self._loop_lock:
            # 如果此前没有 loop，或旧 loop 已关闭，则更新
            if self._loop is None or self._loop.is_closed():
                self._loop = loop
                logger.info("[WS_MANAGER] captured event loop=%s", id(loop))
            return self._loop

    async def connect(self, user_id: int, websocket: WebSocket):
        """
        注册 WS 连接
        """
        await websocket.accept()
        self._users.setdefault(user_id, set()).add(websocket)

        # 捕获事件循环（关键点：确保后台线程未来可投递）
        self._ensure_loop()

        logger.info(
            "[WS_MANAGER] connect user_id=%s total_users=%s conns=%s",
            user_id,
            len(self._users),
            len(self._users.get(user_id, [])),
        )

    def disconnect(self, user_id: int, websocket: WebSocket):
        """
        注销 WS 连接
        """
        conns = self._users.get(user_id)
        if not conns:
            return

        if websocket in conns:
            conns.remove(websocket)

        if not conns:
            self._users.pop(user_id, None)

        logger.info(
            "[WS_MANAGER] disconnect user_id=%s remaining_conns=%s",
            user_id,
            len(self._users.get(user_id, [])),
        )

    async def send_to_user(self, user_id: int, message: dict):
        """
        向指定用户发送 WS 消息（async 版本，供路由/请求上下文直接 await 使用）
        """
        # 在 async 场景下也顺便刷新 loop（例如服务重载/loop 变化）
        self._ensure_loop()

        conns = self._users.get(user_id)

        if not conns:
            logger.warning(
                "[WS_MANAGER] send_to_user SKIPPED (no active ws) user_id=%s event_type=%s",
                user_id,
                message.get("event_type"),
            )
            return

        dead = []

        logger.info(
            "[WS_MANAGER] send_to_user BEGIN user_id=%s conns=%s event_type=%s",
            user_id,
            len(conns),
            message.get("event_type"),
        )

        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(
                    "[WS_MANAGER] send_to_user FAILED user_id=%s err=%s",
                    user_id,
                    e,
                )
                dead.append(ws)

        for ws in dead:
            self.disconnect(user_id, ws)

        logger.info(
            "[WS_MANAGER] send_to_user END user_id=%s sent=%s dead=%s",
            user_id,
            len(conns) - len(dead),
            len(dead),
        )

    def send_to_user_threadsafe(
        self,
        user_id: int,
        message: dict,
        *,
        timeout: float = 2.0,
    ) -> bool:
        """
        线程安全版本：给“后台同步线程/非事件循环线程”使用。
        - 不抛异常（保持 silent-fail 风格）
        - 返回 True/False 表示是否成功投递并在 timeout 内完成
        """
        conns = self._users.get(user_id)
        if not conns:
            logger.warning(
                "[WS_MANAGER] send_to_user_threadsafe SKIPPED (no active ws) user_id=%s event_type=%s",
                user_id,
                message.get("event_type"),
            )
            return False

        loop = self._loop
        if loop is None or loop.is_closed():
            logger.warning(
                "[WS_MANAGER] send_to_user_threadsafe SKIPPED (no loop) user_id=%s event_type=%s",
                user_id,
                message.get("event_type"),
            )
            return False

        try:
            fut = asyncio.run_coroutine_threadsafe(
                self.send_to_user(user_id, message),
                loop,
            )
            fut.result(timeout=timeout)
            return True
        except concurrent.futures.TimeoutError:
            logger.warning(
                "[WS_MANAGER] send_to_user_threadsafe TIMEOUT user_id=%s event_type=%s",
                user_id,
                message.get("event_type"),
            )
            return False
        except Exception as e:
            logger.warning(
                "[WS_MANAGER] send_to_user_threadsafe FAILED user_id=%s event_type=%s err=%s",
                user_id,
                message.get("event_type"),
                e,
            )
            return False

    # ====== 预留能力（当前不启用） ======
    def has_user(self, user_id: int) -> bool:
        """
        判断用户是否存在 WS 连接（用于上层裁决）
        """
        return bool(self._users.get(user_id))


manager = ConnectionManager()
