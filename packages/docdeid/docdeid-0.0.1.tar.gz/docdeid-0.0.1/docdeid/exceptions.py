from enum import Enum, auto


class ErrorHandling(Enum):
    RAISE = auto()
    REDACT = auto()
    WARN_AND_CONTINUE = auto()


class NotDeidentifiedError(Exception):
    """Raises when getting deidentified_text property of a Document, but text is not deidentified"""


class NoTokenizerInitializedError(Exception):
    """Raises when getting tokens property of a Document, when no tokenizer is set"""


class NoMetaDataError(Exception):
    """Raises when getting meta data from a Document, when no meta data is present"""


class NoAnnotatorsInDeidentifierError(Exception):
    """Raises when annotating a text while no annotators are present"""


class DocumentAlreadyDeidentifiedError(Exception):
    """Raises when trying to deidentify a document that is already deidentified"""
