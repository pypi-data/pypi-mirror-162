import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Optional


class BaseStringProcessor(ABC):
    @abstractmethod
    def process_item(self, item: str) -> Optional[str]:
        """Modify the item, or return None to filter it."""


class LowercaseString(BaseStringProcessor):
    def process_item(self, item: str) -> str:
        return item.lower()


class StripString(BaseStringProcessor):
    def process_item(self, item: str) -> str:
        return item.strip()


class RemoveNonAsciiCharacters(BaseStringProcessor):
    @staticmethod
    def _normalize_value(line):
        """Removes all non-ascii characters from a string"""
        line = str(bytes(line, encoding="ascii", errors="ignore"), encoding="ascii")
        return unicodedata.normalize("NFKD", line)

    def process_item(self, item: str) -> str:
        return self._normalize_value(item)


class FilterByLength(BaseStringProcessor):
    def __init__(self, min_len: int):
        self.min_len = min_len

    def process_item(self, item: str) -> Optional[str]:

        if len(item) < self.min_len:
            return None

        return item


class ReplaceValue(BaseStringProcessor):
    def __init__(self, find_value: str, replace_value: str):
        self.find_value = find_value
        self.replace_value = replace_value

    def process_item(self, item: str) -> Optional[str]:
        return item.replace(self.find_value, self.replace_value)


class ReplaceValueRegexp(BaseStringProcessor):
    def __init__(self, find_value: str, replace_value: str):
        self.find_value = find_value
        self.replace_value = replace_value

    def process_item(self, item: str) -> Optional[str]:
        return re.sub(self.find_value, self.replace_value, item)