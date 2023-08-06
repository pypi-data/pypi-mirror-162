from enum import Enum, auto
from typing import Type

from pydantic import BaseModel

from .table import PydandyTable
from .utils import PydandticProxy, PydanticData


class DataMode(str, Enum):
    DIRECTORY = auto()
    FILE = auto()
    IN_MEMORY = auto()


class Data(PydanticData):
    pass


class PydandyData(PydandticProxy):
    support_model = Data

    def __init__(self) -> None:
        super().__init__()
        self._table_map: dict[str, PydandyTable] = {}

    def add_model(self, model: Type[BaseModel], name: str = None):
        model_name = name or model.__name__
        assert model_name not in self, f"A Model called {model_name} already exists!"
        new_table = PydandyTable(model, model_name)
        self._table_map[model_name] = new_table
        self[model_name] = new_table._data

    def get_table(self, name: str):
        return self._table_map.get(name)
