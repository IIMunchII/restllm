import litellm

from typing import Type

from fastapi import status, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from .redis.keys import get_class_name


class ObjectNotFoundException(HTTPException):
    def __init__(self, cls: Type):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ressource of type '{get_class_name(cls)}' not found",
        )


class IndexNotImplemented(HTTPException):
    def __init__(self, cls: Type):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Search index not implemented for type '{get_class_name(cls)}'",
        )


class ObjectAlreadyExistsException(HTTPException):
    def __init__(self, cls: Type):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ressource of type '{get_class_name(cls)}' allready exists",
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = exc.errors()
    formatted_errors = [
        {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": formatted_errors},
    )

async def litellm_badrequest_handler(
    request: Request, exception: litellm.exceptions.BadRequestError
):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "detail": {
                "message": exception.message,
                "error_type": type(exception).__name__,
                "model": exception.model,
                "llm_provider": exception.llm_provider,
            }
        },
    )