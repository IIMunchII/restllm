from fastapi import APIRouter

from ..endpoints import add_crud_route
from ..models import CompletionParameters, CompletionParametersWithMeta

router = APIRouter(
    prefix="/completion",
    tags=["parameters"],
)

add_crud_route(
    router, CompletionParameters, CompletionParametersWithMeta, prefix="/parameters"
)
