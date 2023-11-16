from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .dependencies import get_redis_client
import datetime


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
                    "timestamp": datetime.datetime.now(
                        tz=datetime.timezone.utc
                    ).timestamp(),
                },
            )
            return await call_next(request)
        return await call_next(request)
