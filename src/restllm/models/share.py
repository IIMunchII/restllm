from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, computed_field

from ..models import Chat, PromptTemplate, Prompt
from ..redis.keys import get_class_name
from ..settings import settings


class ShareableObject(str, Enum):
    CHAT = get_class_name(Chat)
    PROMPT_TEMPLAET = get_class_name(PromptTemplate)
    PROMPT = get_class_name(Prompt)


class ShareableObject(BaseModel):
    signature: str = Field(description="Verification signature")
    payload: str = Field(description="Encrypted payload")
    expire_time: int = Field(description="Time in seconds before shared object expires")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Datetime for when the shared object was created",
    )

    @computed_field
    @property
    def uri(self) -> str:
        return f"/{settings.share_prefix}/{self.payload}/{self.signature}"
