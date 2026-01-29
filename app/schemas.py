from pydantic import BaseModel, field_validator

from .auth import BCRYPT_MAX_PASSWORD_BYTES, is_password_too_long


class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if is_password_too_long(value):
            raise ValueError(
                f"Password must be at most {BCRYPT_MAX_PASSWORD_BYTES} bytes / "
                f"Пароль должен быть не длиннее {BCRYPT_MAX_PASSWORD_BYTES} байт."
            )
        return value


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if is_password_too_long(value):
            raise ValueError(
                f"Password must be at most {BCRYPT_MAX_PASSWORD_BYTES} bytes / "
                f"Пароль должен быть не длиннее {BCRYPT_MAX_PASSWORD_BYTES} байт."
            )
        return value


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True
