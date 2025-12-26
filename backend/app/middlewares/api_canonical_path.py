from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import RedirectResponse


class APICanonicalPathMiddleware:
    """
    v1.0.28
    API Canonical Path Middleware

    说明：
    - ASGI 外层 wrapper
    - 早于 FastAPI router / redirect_slashes
    - 早于 account_status
    - 仅治理 /api/*
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            path = scope.get("path", "")

            if path.startswith("/api/") and path != "/api/":
                if path.endswith("/"):
                    canonical_path = path.rstrip("/")

                    query_string = scope.get("query_string", b"")
                    url = canonical_path
                    if query_string:
                        url = f"{canonical_path}?{query_string.decode()}"

                    response = RedirectResponse(
                        url=url,
                        status_code=307,
                    )
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)
