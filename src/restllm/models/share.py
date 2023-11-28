from datetime import datetime
from enum import Enum
from urllib.parse import urljoin
from pydantic import BaseModel, Field, computed_field

from ..models import Chat, PromptTemplate, Prompt
from ..redis.keys import get_class_name
from ..settings import settings

def join_path_segments(path_segments: list[str]):
    return '/'.join([segment.strip('/') for segment in path_segments])

class ShareableClass(str, Enum):
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
        path_segments = [settings.share_prefix, self.payload, self.signature]
        return urljoin(settings.base_url, join_path_segments(path_segments))
