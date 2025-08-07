"""
Password and Passphrase Generator

A secure generator for creating customizable passwords and passphrases
with various character sets, constraints, and accessibility options.
"""

import secrets
import string
from pathlib import Path
from typing import Literal


class PassGenerator:
    """
    A secure password and passphrase generator with customizable options.

    This class provides methods to generate passwords and passphrases with
    specific requirements including character types, minimum counts, and
    accessibility preferences.
    """

    def __init__(self):
        """Initialize the password generator."""
        pass

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
        """
        Generate a random password with customizable character sets and constraints.

        Args:
            length: Total length of the password.
            uppercase: Tuple (enabled, min_count) for uppercase letters.
            lowercase: Tuple (enabled, min_count) for lowercase letters.
            numbers: Tuple (enabled, min_count) for digits.
            special_characters: Tuple (enabled, min_count, list of special chars or 'auto').
            include: List of additional characters to include (default: None).
            exclude: List of characters to exclude (default: None).
            easy_to: 'read' for easy-to-read, 'type' for easy-to-type (default: 'read').

        Returns:
            A generated password string.

        Raises:
            ValueError: If length is invalid or requirements cannot be met.
        """
        if include is None:
            include = []
        if exclude is None:
            exclude = []
        if length <= 0:
            raise ValueError("Password length must be greater than 0")

        # Define character sets
        char_sets = {}

        if uppercase[0]:
            if easy_to == "type":
                char_sets["uppercase"] = (
                    "ABCDEFGHJKLMNPQRSTUVWXYZ"  # Remove I, O for easier typing
                )
            else:
                char_sets["uppercase"] = string.ascii_uppercase

        if lowercase[0]:
            if easy_to == "type":
                char_sets["lowercase"] = (
                    "abcdefghjkmnpqrstuvwxyz"  # Remove i, l, o for easier typing
                )
            else:
                char_sets["lowercase"] = string.ascii_lowercase

        if numbers[0]:
            if easy_to == "read":
                char_sets["numbers"] = "23456789"  # Remove 0, 1 for easier reading
            else:
                char_sets["numbers"] = string.digits

        if special_characters[0]:
            special_chars_value = special_characters[2]
            if special_chars_value == "auto":
                if easy_to == "type":
                    char_sets["special"] = "!@#$%&*+-="  # Easier to type special chars
                elif easy_to == "read":
                    char_sets["special"] = "!@#$%^&*-+="  # Remove ambiguous chars
                else:
                    char_sets["special"] = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            else:
                char_sets["special"] = "".join(special_chars_value)

        # Add custom include characters
        if include:
            char_sets["custom"] = "".join(include)

        # Remove excluded characters from all sets
        if exclude:
            exclude_set = set(exclude)
            for key in char_sets:
                char_sets[key] = "".join(
                    c for c in char_sets[key] if c not in exclude_set
                )

        # Check if we have enough character types for minimum requirements
        min_chars_needed = 0
        for param in [uppercase, lowercase, numbers, special_characters]:
            enabled = param[0]
            min_count = param[1]
            if enabled and min_count > 0:
                min_chars_needed += min_count

        if min_chars_needed > length:
            # Try to auto-correct by reducing min_count for non-numbers to 0 if possible
            # Only keep numbers min_count if all others can be set to 0
            # This is a simple fix for the common PIN use-case
            numbers_enabled, numbers_min = numbers[0], numbers[1]
            if numbers_enabled and numbers_min == length:
                # Set all other min_counts to 0
                uppercase = (False, 0)
                lowercase = (False, 0)
                special_characters = (False, 0, special_characters[2])
                min_chars_needed = numbers_min
            else:
                raise ValueError(
                    f"Password length {length} is too short for minimum character requirements ({min_chars_needed})"
                )

        if not char_sets:
            raise ValueError("No character sets available for password generation")

        # Build password ensuring minimum character requirements
        password_chars = []

        # Add minimum required characters from each enabled set
        for (char_type, min_count), set_name in zip(
            [
                ("uppercase", uppercase[1]),
                ("lowercase", lowercase[1]),
                ("numbers", numbers[1]),
                ("special", special_characters[1]),
            ],
            ["uppercase", "lowercase", "numbers", "special"],
        ):
            enabled = False
            if char_type == "uppercase":
                enabled = uppercase[0]
            elif char_type == "lowercase":
                enabled = lowercase[0]
            elif char_type == "numbers":
                enabled = numbers[0]
            elif char_type == "special":
                enabled = special_characters[0]
            if enabled and set_name in char_sets and char_sets[set_name]:
                chars = char_sets[set_name]
                for _ in range(min_count):
                    password_chars.append(secrets.choice(chars))

        # Fill remaining length with random characters from all available sets
        all_chars = "".join(char_sets.values())
        if not all_chars:
            raise ValueError("No valid characters available after applying exclusions")

        while len(password_chars) < length:
            password_chars.append(secrets.choice(all_chars))

        # Shuffle the password to avoid predictable patterns
        secrets.SystemRandom().shuffle(password_chars)

        # Ensure at least the minimum number of each required character type is present
        # (already enforced above, but double-check for special)
        if special_characters[0] and special_characters[1] > 0:
            special_set = set(char_sets.get("special", ""))
            if special_set:
                count = sum(1 for c in password_chars if c in special_set)
                if count < special_characters[1]:
                    # Replace random chars with special chars to meet requirement
                    for _ in range(special_characters[1] - count):
                        idx = secrets.randbelow(len(password_chars))
                        password_chars[idx] = secrets.choice(list(special_set))

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
        """
        Generate a random passphrase using words, with optional numbers and special characters.

        Args:
            length: Number of words in the passphrase.
            numbers: Tuple (enabled, count) for numbers to add.
            special_characters: Tuple (enabled, count, list of special chars or 'auto').
            include: List of additional words to include (default: None).
            exclude: List of characters to exclude from words and specials (default: None).
            easy_to: 'read' for easy-to-read, 'type' for easy-to-type (default: 'read').
            separator: String to join words and extras (default: space).

        Returns:
            A generated passphrase string.
        """
        if include is None:
            include = []
        if exclude is None:
            exclude = []
        if length <= 0:
            raise ValueError("Passphrase length must be greater than 0")

        words_file = Path(__file__).parent / "data" / "words.txt"
        with open(words_file, "r", encoding="utf-8") as f:
            word_list = [word.strip() for word in f.readlines() if word.strip()]

        # Filter words based on exclusions
        if exclude:
            exclude_set = set(exclude)
            word_list = [
                word
                for word in word_list
                if not any(char in exclude_set for char in word)
            ]

        # Add custom words from include list
        if include:
            word_list.extend(include)

        if not word_list:
            raise ValueError("No valid words available after applying exclusions")

        passphrase_words = []
        for _ in range(length):
            word = secrets.choice(word_list)
            if easy_to == "type":
                word = word.lower()  # Easier to type
            elif easy_to == "read":
                word = word.capitalize()  # Easier to read
            passphrase_words.append(word)

        extras = []
        # Add numbers if required
        if numbers[0] and numbers[1] > 0:
            for _ in range(numbers[1]):
                if easy_to == "read":
                    num = str(secrets.randbelow(8) + 2)  # 2-9
                else:
                    num = str(secrets.randbelow(10))  # 0-9
                extras.append(num)

        # Add special characters if required
        if special_characters[0] and special_characters[1] > 0:
            special_chars_value = special_characters[2]
            if special_chars_value == "auto":
                if easy_to == "type":
                    special_chars = "!@#$%&*+-="
                elif easy_to == "read":
                    special_chars = "!@#$%^&*-+="
                else:
                    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            else:
                special_chars = "".join(special_chars_value)
            # Remove excluded characters
            if exclude:
                exclude_set = set(exclude)
                special_chars = "".join(
                    c for c in special_chars if c not in exclude_set
                )
            if special_chars:
                for _ in range(special_characters[1]):
                    extras.append(secrets.choice(special_chars))

        # Combine and shuffle
        all_parts = passphrase_words + extras
        secrets.SystemRandom().shuffle(all_parts)

        # Ensure at least the required number of numbers and special chars are present
        if numbers[0] and numbers[1] > 0:
            num_count = sum(1 for part in all_parts if part.isdigit())
            if num_count < numbers[1]:
                for _ in range(numbers[1] - num_count):
                    idx = secrets.randbelow(len(all_parts))
                    all_parts[idx] = (
                        str(secrets.randbelow(8) + 2)
                        if easy_to == "read"
                        else str(secrets.randbelow(10))
                    )
        if special_characters[0] and special_characters[1] > 0:
            special_chars_value = special_characters[2]
            if special_chars_value == "auto":
                if easy_to == "type":
                    special_chars = "!@#$%&*+-="
                elif easy_to == "read":
                    special_chars = "!@#$%^&*-+="
                else:
                    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            else:
                special_chars = "".join(special_chars_value)
            if exclude:
                exclude_set = set(exclude)
                special_chars = "".join(
                    c for c in special_chars if c not in exclude_set
                )
            special_set = set(special_chars)
            spec_count = sum(
                1 for part in all_parts if any(c in special_set for c in part)
            )
            if spec_count < special_characters[1]:
                for _ in range(special_characters[1] - spec_count):
                    idx = secrets.randbelow(len(all_parts))
                    all_parts[idx] = secrets.choice(list(special_set))

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
