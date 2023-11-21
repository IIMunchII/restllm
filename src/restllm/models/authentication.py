from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    computed_field,
    model_validator,
    ValidationError,
)
from ..models.base import User

from ..cryptography.authentication import get_password_hash


def get_user_email_key(email: str) -> str:
    return f"UserEmail:{email}"


class UserWithPasswordHash(User):
    hashed_password: str

    def get_user_data(self) -> dict:
        return self.model_dump(exclude=["hashed_password"])


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class UserSignUp(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: SecretStr
    confirm_password: SecretStr

    def create_user(self, id: str) -> UserWithPasswordHash:
        new_user = {
            "id": id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "hashed_password": get_password_hash(self.password.get_secret_value()),
        }

        return UserWithPasswordHash(**new_user)

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ChangePassword":
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("Both fields for new password must match")
        return self

    @computed_field(return_type=str)
    @property
    def email_key(self) -> str:
        return get_user_email_key(self.email)


class ChangePassword(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
    confirm_new_password: SecretStr

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ChangePassword":
        pw1 = self.new_password
        pw2 = self.confirm_new_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("Both fields for new password must match")
        return self

    def get_new_password_hash(self) -> str:
        return get_password_hash(self.new_password.get_secret_value())
