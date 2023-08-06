"""Custom types for phrase-translator, mostly immutable data containers."""
import json
from enum import Enum


class Language(str, Enum):
    """The languages currently supported by phrase-translator."""

    ENGLISH = "en"
    GERMAN = "de"
    UNKNOWN = "unknown"

    def __eq__(self, other):
        if not isinstance(other, Language):
            return False

        return self.value == other.value

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.value)


class Translation:
    """A wrapper object for a single translation.
    Encapsulates source and target phrase as well as their respective
    languages."""

    def __init__(
        self,
        source_phrase: str,
        target_phrase: str,
        source_lang: Language,
        target_lang: Language,
    ) -> None:
        self.__source_phrase = source_phrase
        self.__target_phrase = target_phrase
        self.__source_lang = source_lang
        self.__target_lang = target_lang

    def __str__(self) -> str:
        return self.to_json_string()

    def __repr__(self) -> str:
        return self.to_json_string()

    def __eq__(self, other):
        if not isinstance(other, Translation):
            return False

        return (
            self.__source_phrase == other.get_source_phrase()
            and self.__target_phrase == other.get_target_phrase()
            and self.__source_lang == other.get_source_lang()
            and self.__target_lang == other.get_target_lang()
        )

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(
            (
                self.__source_phrase,
                self.__target_phrase,
                self.__source_lang,
                self.__target_lang,
            )
        )

    def get_source_phrase(self) -> str:
        """Simple getter."""

        return self.__source_phrase

    def get_target_phrase(self) -> str:
        """Simple getter."""

        return self.__target_phrase

    def get_source_lang(self) -> Language:
        """Simple getter."""

        return self.__source_lang

    def get_target_lang(self) -> Language:
        """Simple getter."""

        return self.__target_lang

    def to_json_string(self) -> str:
        """Returns a JSON string representing self."""

        return json.dumps(self.__dict__)
