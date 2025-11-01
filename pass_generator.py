import secrets
import string
from pathlib import Path
from typing import Literal
from functools import cached_property


class PassGenerator:
    EASY_TYPE_UPPERCASE = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    EASY_TYPE_LOWERCASE = "abcdefghjkmnpqrstuvwxyz"
    EASY_READ_NUMBERS = "23456789"
    EASY_TYPE_SPECIAL = "!@#$%&*+-="
    EASY_READ_SPECIAL = "!@#$%^&*-+="
    FULL_SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    @cached_property
    def word_list(self) -> list[str]:
        words_file = Path(__file__).parent / "data" / "words.txt"
        with open(words_file, encoding="utf-8") as f:
            return [word.strip() for word in f if word.strip()]

    def _get_special_chars(
        self, easy_to: str, custom_chars: list[str] | Literal["auto"]
    ) -> str:
        if custom_chars != "auto":
            return "".join(custom_chars)

        match easy_to:
            case "type":
                return self.EASY_TYPE_SPECIAL
            case "read":
                return self.EASY_READ_SPECIAL
            case _:
                return self.FULL_SPECIAL

    def _build_char_sets(
        self,
        uppercase: bool,
        lowercase: bool,
        numbers: bool,
        special: bool,
        special_chars: list[str] | Literal["auto"],
        easy_to: str,
        include: list[str],
        exclude: list[str],
    ) -> dict[str, str]:
        char_sets = {}

        if uppercase:
            char_sets["uppercase"] = (
                self.EASY_TYPE_UPPERCASE
                if easy_to == "type"
                else string.ascii_uppercase
            )

        if lowercase:
            char_sets["lowercase"] = (
                self.EASY_TYPE_LOWERCASE
                if easy_to == "type"
                else string.ascii_lowercase
            )

        if numbers:
            char_sets["numbers"] = (
                self.EASY_READ_NUMBERS if easy_to == "read" else string.digits
            )

        if special:
            char_sets["special"] = self._get_special_chars(easy_to, special_chars)

        if include:
            char_sets["custom"] = "".join(include)

        if exclude:
            exclude_set = set(exclude)
            char_sets = {
                key: "".join(c for c in value if c not in exclude_set)
                for key, value in char_sets.items()
                if value
            }

        return char_sets

    def generate_password(
        self,
        length: int,
        uppercase: tuple[bool, int] = (True, 1),
        lowercase: tuple[bool, int] = (True, 1),
        numbers: tuple[bool, int] = (True, 1),
        special_characters: tuple[bool, int, list[str] | Literal["auto"]] = (
            True,
            1,
            "auto",
        ),
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        easy_to: Literal["read", "type"] = "read",
    ) -> str:
        include = include or []
        exclude = exclude or []

        if length <= 0:
            raise ValueError("Password length must be greater than 0")

        min_chars_needed = sum(
            [
                uppercase[1] if uppercase[0] else 0,
                lowercase[1] if lowercase[0] else 0,
                numbers[1] if numbers[0] else 0,
                special_characters[1] if special_characters[0] else 0,
            ]
        )

        if min_chars_needed > length:
            if numbers[0] and numbers[1] == length:
                uppercase = (False, 0)
                lowercase = (False, 0)
                special_characters = (False, 0, special_characters[2])
                min_chars_needed = numbers[1]
            else:
                raise ValueError(
                    f"Password length {length} is too short for minimum character requirements ({min_chars_needed})"
                )

        char_sets = self._build_char_sets(
            uppercase[0],
            lowercase[0],
            numbers[0],
            special_characters[0],
            special_characters[2],
            easy_to,
            include,
            exclude,
        )

        if not char_sets:
            raise ValueError("No character sets available for password generation")

        all_chars = "".join(char_sets.values())
        if not all_chars:
            raise ValueError("No valid characters available after applying exclusions")

        password_chars = []

        if uppercase[0] and "uppercase" in char_sets and char_sets["uppercase"]:
            password_chars.extend(
                secrets.choice(char_sets["uppercase"]) for _ in range(uppercase[1])
            )

        if lowercase[0] and "lowercase" in char_sets and char_sets["lowercase"]:
            password_chars.extend(
                secrets.choice(char_sets["lowercase"]) for _ in range(lowercase[1])
            )

        if numbers[0] and "numbers" in char_sets and char_sets["numbers"]:
            password_chars.extend(
                secrets.choice(char_sets["numbers"]) for _ in range(numbers[1])
            )

        if special_characters[0] and "special" in char_sets and char_sets["special"]:
            password_chars.extend(
                secrets.choice(char_sets["special"])
                for _ in range(special_characters[1])
            )

        password_chars.extend(
            secrets.choice(all_chars) for _ in range(length - len(password_chars))
        )

        secrets.SystemRandom().shuffle(password_chars)

        return "".join(password_chars)

    def generate_passphrase(
        self,
        length: int,
        numbers: tuple[bool, int] = (False, 0),
        special_characters: tuple[bool, int, list[str] | Literal["auto"]] = (
            False,
            0,
            ["@"],
        ),
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        easy_to: Literal["read", "type"] = "read",
        separator: str = " ",
    ) -> str:
        include = include or []
        exclude = exclude or []

        if length <= 0:
            raise ValueError("Passphrase length must be greater than 0")

        word_list = self.word_list.copy()
        if exclude:
            exclude_set = set(exclude)
            word_list = [
                word
                for word in word_list
                if not any(char in exclude_set for char in word)
            ]

        if include:
            word_list.extend(include)

        if not word_list:
            raise ValueError("No valid words available after applying exclusions")

        match easy_to:
            case "type":
                passphrase_words = [
                    secrets.choice(word_list).lower() for _ in range(length)
                ]
            case _:
                passphrase_words = [
                    secrets.choice(word_list).capitalize() for _ in range(length)
                ]

        extras = []

        if numbers[0] and numbers[1] > 0:
            num_range = range(2, 10) if easy_to == "read" else range(10)
            extras.extend(str(secrets.choice(num_range)) for _ in range(numbers[1]))

        if special_characters[0] and special_characters[1] > 0:
            special_chars = self._get_special_chars(easy_to, special_characters[2])
            if exclude:
                special_chars = "".join(c for c in special_chars if c not in exclude)
            if special_chars:
                extras.extend(
                    secrets.choice(special_chars) for _ in range(special_characters[1])
                )

        all_parts = passphrase_words + extras
        secrets.SystemRandom().shuffle(all_parts)

        return separator.join(all_parts)


if __name__ == "__main__":
    gen = PassGenerator()
    print("Example password:")
    pw = gen.generate_password(
        length=30,
        uppercase=(True, 2),
        lowercase=(True, 2),
        numbers=(True, 2),
        special_characters=(True, 3, ["@", "#", "$"]),
        easy_to="read",
    )
    print(pw)

    print("\nExample passphrase:")
    ph = gen.generate_passphrase(
        length=5,
        numbers=(True, 1),
        special_characters=(True, 1, "auto"),
        easy_to="read",
        separator="-",
    )
    print(ph)
