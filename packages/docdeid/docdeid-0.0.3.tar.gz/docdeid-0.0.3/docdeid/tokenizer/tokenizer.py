import re
from abc import ABC, abstractmethod

from docdeid.config import ConfigMixin
from docdeid.describe import DescribeMixin
from docdeid.tokenizer.token import Token


class BaseTokenizer(ABC, DescribeMixin, ConfigMixin):
    """A tokenizer tokenizes a piece of text."""

    @abstractmethod
    def tokenize(self, text: str) -> list[Token]:
        """
        Tokenize the text.

        Args:
            text: The input text.

        Returns: A list of tokens, based on the input text.

        """


class SpaceSplitTokenizer(BaseTokenizer):
    """Tokenizer that splits text whenever a whitespace is present."""

    def tokenize(self, text: str) -> list[Token]:
        return [
            Token(text=match.group(0), start_char=match.start(), end_char=match.end())
            for match in re.finditer(r"[^\s]+", text)
        ]
