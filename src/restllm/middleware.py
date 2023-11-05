from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .dependencies import get_redis_client
from .models.base import User
import datetime


class UserSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        test_user = User(
            id="munch",
            first_name="Jonas",
            last_name="Høgh",
            email="jonash@email.fo",
        )
        session_cookie = request.cookies.get("session_cookie", test_user)
        if session_cookie:
            request.state.user = session_cookie
        else:
            request.state.user = None
        return await call_next(request)


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        if not request.url.path.startswith(("/docs", "/openapi.json", "/redoc")):
            async_gen = get_redis_client()
            redis_client = await async_gen.__anext__()
            await redis_client.xadd(
                "access_log_stream",
                {
                    "path": request.url.path,
                    "timestamp": datetime.datetime.utcnow().timestamp(),
                    "user": "munch",
                },
            )
            return await call_next(request)
        return await call_next(request)
