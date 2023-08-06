from dataclasses import dataclass


@dataclass(frozen=True)
class Annotation:
    """
    An annotation is a matched entity in a text, with a text, a start- and end index (character),
    and a category.
    """

    text: str
    start_char: int
    end_char: int
    category: str
