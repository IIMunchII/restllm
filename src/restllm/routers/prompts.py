import redis.asyncio as redis
from pydantic import ValidationError

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import get_redis_client, build_get_instance_key
from ..endpoints import add_crud_route
from ..models import (
    Prompt,
    PromptTemplate,
    PromptTemplateWithMeta,
    PromptWithMeta,
)
from ..redis.commands import get_instance
from ..exceptions import ObjectNotFoundException

router = APIRouter(
    prefix="/prompts",
    tags=["prompts"],
)

add_crud_route(router, PromptTemplate, PromptTemplateWithMeta, prefix="/template")
add_crud_route(router, Prompt, PromptWithMeta, prefix="/prompt")


@router.post("/template/{id}/render", response_model=Prompt)
async def render_prompt_template(
    parameters: dict[str, str | int | list | dict],
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_instance_key(PromptTemplate)),
) -> Prompt:
    template_data = await get_instance(
        redis_client=redis_client,
        key=key,
    )
    if not template_data:
        raise ObjectNotFoundException(PromptTemplate)
    prompt_template = PromptTemplate.model_validate(template_data.get("object"))

    try:
        return prompt_template.render(parameters)
    except ValidationError as exec:
        return JSONResponse(content={"detail": exec.errors()}, status_code=422)
