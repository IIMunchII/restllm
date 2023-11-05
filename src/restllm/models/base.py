import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, EmailStr, computed_field


class CustomInstructions(BaseModel):
    response_instruction: Optional[str] = Field(
        default="", description="Custom instructions how the LLM should respond"
    )
    preference_instruction: Optional[str] = Field(
        default="", description="Custom instructions for user preferences"
    )
    enabled: bool = Field(
        default=False, description="Whether custom instructions are enabled for chats"
    )


class UserProfile(BaseModel):
    custom_instructions: CustomInstructions = Field(
        default_factory=CustomInstructions,
        description="Custom instructions to use in chat.",
    )


class User(BaseModel):
    id: str = Field(
        description="Unique identifier for a given user", exclude=True, frozen=True
    )
    first_name: str = Field(
        description="First name of the user", examples=["Alice"], frozen=True
    )
    last_name: str = Field(
        description="Last name of the user", examples=["Wonderer"], frozen=True
    )
    email: EmailStr = Field(description="Valid email for the user", frozen=True)

    @computed_field(return_type=str)
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_key(self) -> str:
        return f"{self.__class__.__name__}:{self.id}"


class Datetime(BaseModel):
    datetime_iso: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        description="Datetime string in iso format",
    )
    timezone: str = Field(
        default_factory=lambda: str(datetime.timezone.utc),
        frozen=True,
        examples=["UTC"],
    )

    @computed_field(return_type=float)
    @property
    def timestamp(self) -> float:
        return self.datetime_iso.timestamp()


class MetaModel(BaseModel):
    id: int = Field(gt=0, examples=[1, 2, 3])
    class_name: str
    owner: str
    object: Any
    created_at: Datetime = Field(default_factory=Datetime)
    updated_at: Datetime = Field(default_factory=Datetime)


class UserProfileWithMeta(MetaModel):
    object: UserProfile
