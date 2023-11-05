from fastapi import APIRouter

from ..models import functions

router = APIRouter(
    prefix="/functions",
    tags=["functions"],
)


@router.get("", response_model=list[functions.Function])
def get_functions():
    return functions.get_all_function_schemas()


@router.get("/{name}", response_model=functions.Function)
def get_functions(name: functions.FunctionName):
    return functions.get_function_classes()[name].function_schema
