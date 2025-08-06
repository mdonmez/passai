from typing import Optional, Literal
from pydantic import BaseModel, Field


class PasswordParams(BaseModel):
    length: int = Field(..., gt=0, description="Total length of the password")
    uppercase: tuple[bool, int] = (True, 1)
    lowercase: tuple[bool, int] = (True, 1)
    numbers: tuple[bool, int] = (True, 1)
    special_characters: tuple[bool, int, list[str] | Literal["auto"]] = (
        True,
        1,
        "auto",
    )
    include: Optional[list[str]] = None
    exclude: Optional[list[str]] = None
    easy_to: Literal["read", "type"] = "read"


class PassphraseParams(BaseModel):
    length: int = Field(..., gt=0, description="Number of words in the passphrase")
    numbers: tuple[bool, int] = (False, 0)
    special_characters: tuple[bool, int, list[str] | Literal["auto"]] = (
        False,
        0,
        "auto",
    )
    include: Optional[list[str]] = None
    exclude: Optional[list[str]] = None
    easy_to: Literal["read", "type"] = "read"
    separator: str = " "


class PassParams(BaseModel):
    type: Literal["password", "passphrase"]
    password: Optional[PasswordParams] = None
    passphrase: Optional[PassphraseParams] = None
