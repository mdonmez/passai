from typing import Literal
from pydantic import BaseModel, Field


class PasswordParams(BaseModel):
    length: int = Field(..., gt=0, description="Total length of the password")
    uppercase: tuple[bool, int] = Field(
        default=(True, 1), description="Include uppercase letters"
    )
    lowercase: tuple[bool, int] = Field(
        default=(True, 1), description="Include lowercase letters"
    )
    numbers: tuple[bool, int] = Field(default=(True, 1), description="Include numbers")
    special_characters: tuple[bool, int, list[str] | Literal["auto"]] = Field(
        default=(True, 1, "auto"), description="Include special characters"
    )
    include: list[str] | None = Field(default=None, description="Characters to include")
    exclude: list[str] | None = Field(default=None, description="Characters to exclude")
    easy_to: Literal["read", "type"] = Field(
        default="read", description="Optimization preference"
    )


class PassphraseParams(BaseModel):
    length: int = Field(..., gt=0, description="Number of words in the passphrase")
    numbers: tuple[bool, int] = Field(default=(False, 0), description="Include numbers")
    special_characters: tuple[bool, int, list[str] | Literal["auto"]] = Field(
        default=(False, 0, "auto"), description="Include special characters"
    )
    include: list[str] | None = Field(default=None, description="Words to include")
    exclude: list[str] | None = Field(default=None, description="Characters to exclude")
    easy_to: Literal["read", "type"] = Field(
        default="read", description="Optimization preference"
    )
    separator: str = Field(default=" ", description="Word separator")


class PassParams(BaseModel):
    type: Literal["password", "passphrase"] = Field(
        ..., description="Type of pass to generate"
    )
    password: PasswordParams | None = Field(
        default=None, description="Password configuration"
    )
    passphrase: PassphraseParams | None = Field(
        default=None, description="Passphrase configuration"
    )
