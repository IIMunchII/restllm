from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from ..settings import settings

pwd_context = CryptContext(
    schemes=[settings.password_hash_algorithm],
    deprecated="auto",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/authentication/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now(tz=timezone.utc) + expires_delta,
        }
    )
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


async def create_tokens(data: dict) -> tuple[str, str]:
    access_token = create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
    )

    return access_token, refresh_token
