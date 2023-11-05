from fastapi import FastAPI
from .dependencies import shutdown, startup
from .middleware import AccessLogMiddleware, UserSessionMiddleware
from .routers import (
    chats,
    events,
    prompts,
    share,
    completion_parameters,
    users,
    functions,
)

app = FastAPI(
    title="REST LLM",
    description="REST API for interacting with Large Language Models. Runs on RedisStack (https://redis.io/docs/about/about-stack/) and LiteLLM (https://litellm.ai). The REST API is a work in progress",
)

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

# V1 of API
app.include_router(chats.router, prefix="/v1")
app.include_router(events.router, prefix="/v1")
app.include_router(share.router, prefix="/v1")
app.include_router(prompts.router, prefix="/v1")
app.include_router(completion_parameters.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(functions.router, prefix="/v1")

app.add_middleware(UserSessionMiddleware)
app.add_middleware(AccessLogMiddleware)
