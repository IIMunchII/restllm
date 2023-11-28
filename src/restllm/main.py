from fastapi import FastAPI, Request
from .dependencies import shutdown, startup
from .middleware import AccessLogMiddleware
from .routers import (
    chats,
    events,
    prompts,
    share,
    completion_parameters,
    users,
    functions,
    authentication,
)
from .exceptions import validation_exception_handler
from pydantic import ValidationError

app = FastAPI(
    title="REST LLM",
    description="REST API for interacting with Large Language Models. Runs on RedisStack (https://redis.io/docs/about/about-stack/) and LiteLLM (https://litellm.ai). The REST API is a work in progress",
)

# Event handlers
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

# Exception handlers
app.add_exception_handler(ValidationError, validation_exception_handler)


# V1 of API
app.include_router(chats.router, prefix="/v1")
app.include_router(events.router, prefix="/v1")
app.include_router(share.router, prefix="/v1")
app.include_router(prompts.router, prefix="/v1")
app.include_router(completion_parameters.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(functions.router, prefix="/v1")
app.include_router(authentication.router, prefix="/v1")

app.add_middleware(AccessLogMiddleware)
