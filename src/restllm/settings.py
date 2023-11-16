from pydantic_settings import BaseSettings
from pydantic import Field, RedisDsn, HttpUrl


class Settings(BaseSettings):
    secret_key: str = "09u23lkansld920394u23,njsldk"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    refresh_token_expire_minutes: int = 240
    shared_object_expire: int = Field(
        default=3600,
        description="Time in seconds before shared objects expire",
    )
    share_prefix: str = Field(
        default="/share",
        description="APIRouter prefix for the 'share' route",
    )
    redis_dsn: RedisDsn = "redis://localhost:6379/0"
    ollama_base_url: HttpUrl = "http://localhost:11434"


settings = Settings()
