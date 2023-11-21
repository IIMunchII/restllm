import redis.asyncio as redis
from fastapi import APIRouter, BackgroundTasks

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..tasks.email import send_email_verification_url
from ..cryptography.authentication import create_tokens
from ..cryptography.keys import get_fernet
from ..cryptography.secure_url import (
    decrypt_payload,
    generate_secure_url,
    payload_is_valid,
)
from ..models.authentication import Token, UserSignUp, ChangePassword
from ..endpoints.authentication import create_user_instance
from ..models import User
from ..dependencies import (
    get_redis_client,
    authenticate_user,
    signup_form,
    change_password_form,
    create_instance_id,
    decode_user_token,
    get_user,
)
from ..redis.keys import get_class_name
from ..types import paths

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
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not yet verified",
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
    background_tasks: BackgroundTasks,
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

    fernet = await get_fernet(redis_client)
    signed_data = generate_secure_url(fernet, {"user_id": instance_id})
    verification_url = f"http://localhost:8000/v1/authentication/verify-email/{signed_data.get('payload')}/{signed_data.get('signature')}"
    background_tasks.add_task(
        send_email_verification_url,
        signup_data.email,
        verification_url,
    )

    return instance


@router.get("/verify-email/{payload}/{signature}")
async def verify_email(
    payload: str = paths.payload_path,
    signature: str = paths.signature_path,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    fernet = await get_fernet(redis_client)
    if not payload_is_valid(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request",
        )
    user_id: int = decrypt_payload(fernet, payload).get("user_id")
    user_key = f"{get_class_name(User)}:{user_id}"
    updated = await redis_client.json().set(user_key, "$.verified", True, xx=True)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password-change")
async def change_password(
    password_change: ChangePassword = Depends(change_password_form),
    user: User = Depends(get_user),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    await authenticate_user(
        user.email,
        password_change.old_password.get_secret_value(),
        redis_client,
    )

    updated = redis_client.json().set(
        user.get_key(),
        "$.hashed_password",
        password_change.get_new_password_hash(),
        xx=True,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password update failed",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
