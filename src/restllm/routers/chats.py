from fastapi import APIRouter

from ..endpoints import add_crud_route
from ..models import Chat, ChatWithMeta
from . import completion, messages

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)
router.include_router(
    messages.router,
    prefix="/{id}",
)
router.include_router(
    completion.router,
    prefix="/{id}",
)


add_crud_route(router, Chat, ChatWithMeta)
