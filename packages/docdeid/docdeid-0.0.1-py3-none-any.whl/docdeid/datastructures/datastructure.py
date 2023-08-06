from abc import ABC


class Datastructure(ABC):
    pass


class DatastructCollection:
    def __init__(self):
        self.datastructures = {}

    def add_datastructure(self, name: str, datastructure: Datastructure):
        self.datastructures[name] = datastructure

    def remove_datastructure(self, name: str):
        del self.datastructures[name]

    def __getitem__(self, name: str):
        return self.datastructures[name]

    def __setitem__(self, key, value):
        self.add_datastructure(name=key, datastructure=value)
