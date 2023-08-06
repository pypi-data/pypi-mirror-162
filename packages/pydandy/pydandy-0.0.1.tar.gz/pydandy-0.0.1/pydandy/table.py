from typing import Callable, Type

from pydantic import BaseModel

from .exceptions import ExistingRecord, NonexistentRecord
from .results import PydandyResults
from .utils import PydandticProxy, PydanticData


class Table(PydanticData):
    pass


class PydandyTable(PydandticProxy):
    support_model = Table

    def __init__(
        self,
        model: Type[BaseModel],
        model_name: str,
        *args,
        **kwargs,
    ) -> None:
        self._model = model
        self._model_name = model_name
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"PydandyTable<{self._model_name}>"

    def add(self, obj: BaseModel):
        assert isinstance(obj, self._model), f"Invalid type. Cannot add {obj.__class__} to {self}"
        record_id = hash(obj)
        if record_id in self:
            raise ExistingRecord
        self[record_id] = obj.copy()

    def get(self, id: int) -> BaseModel:
        if id not in self:
            raise NonexistentRecord
        return self[id].copy()

    def filter(self, filter: Callable) -> PydandyResults:
        return PydandyResults(records=[record.copy() for record in self.values() if filter(record)])

    def update(self, obj: BaseModel):
        assert isinstance(obj, self._model), f"Invalid type. Cannot add {obj.__class__} to {self}"
        record_id = hash(obj)
        if record_id not in self:
            raise NonexistentRecord
        self[record_id] = obj.copy()

    def delete(self, id: int):
        if id not in self:
            raise NonexistentRecord
        del self[id]
