import json
from typing import Optional


def _read_config_json() -> dict:
    """Tries to read from config json"""

    try:
        with open("config.json", "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return {}


class Config:
    """
    A config object is a light wrapper round a dict object.
    Args:
        items: A dict, will superseed any items read from config.json (if present)
    """

    def __init__(self, items: Optional[dict] = None):
        self._items = _read_config_json()

        if items is not None:
            self._items |= items

    def __getitem__(self, key):
        """Get item by key."""

        try:
            return self._items[key]

        except KeyError:
            raise KeyError(
                f"Trying to get an item from config with key {key} that is not present"
            )

    def update(self, items: dict):
        """Add or overwrite items."""
        self._items |= items

    def describe(self):
        """Default describe, by listing the items"""
        items = ", ".join(f"{key}={value}" for key, value in self._items.items())
        return f"Config({items}"


class ConfigMixin:
    """Inherit from this class to enable config."""

    def __init__(self):
        self._config = None

    def set_config(self, config: Config):
        """Set config. Must be used before the mixin is useful."""
        self._config = config

    def _get_config_item(self, key: str):

        try:
            return self._config[key]
        except TypeError as ex:
            raise KeyError(
                f"Trying to get config item with key = {key}, but no Config is present. "
                f"You need to use the set_config() function of a ConfigMixin class before using _get_config_item()"
            ) from ex
