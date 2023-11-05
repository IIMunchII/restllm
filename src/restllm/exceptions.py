from typing import Type

from fastapi import status, HTTPException
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
