from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """A token is a piece of a text, determined by the tokenizer."""

    text: str
    start_char: int
    end_char: int
