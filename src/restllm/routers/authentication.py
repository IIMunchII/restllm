import redis.asyncio as redis

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..cryptography.authentication import create_tokens
from ..models.authentication import Token, UserSignUp
from ..endpoints.authentication import create_user_instance
from ..models import User
from ..dependencies import (
    get_redis_client,
    authenticate_user,
    signup_form,
    create_instance_id,
    decode_user_token,
)
from fastapi import APIRouter
from ..redis.keys import get_class_name

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"],
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    user = await authenticate_user(form_data.username, form_data.password, redis_client)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = await create_tokens(user.get_user_data())

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(token_data: dict = Depends(decode_user_token)):
    access_token, refresh_token = await create_tokens(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/signup", response_model=User)
async def user_signup(
    signup_data: UserSignUp = Depends(signup_form),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    user_exists = await redis_client.exists(signup_data.email_key)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )

    instance_id = await create_instance_id(redis_client, get_class_name(User))

    created, instance = await create_user_instance(
        redis_client,
        signup_data.create_user(instance_id),
        signup_data.email_key,
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed",
        )
    return instance
