from typing import Literal

Language = Literal["en", "kr"]


def get_language_name(language: Language) -> str:
    """Get the display name for a language code."""
    return "English" if language == "en" else "Korean"
