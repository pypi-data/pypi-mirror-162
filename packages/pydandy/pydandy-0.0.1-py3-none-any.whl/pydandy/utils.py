from typing import Type

from pydantic import BaseModel


class PydanticData(BaseModel):
    __root__: dict[str | int, BaseModel] = {}


class PydandticProxy:
    support_model: Type[PydanticData] = PydanticData

    def __init__(self) -> None:
        self._data = self.support_model()

    def json(self, *args, **kwargs):
        return self._data.json(*args, **kwargs)

    def keys(self):
        return self._data.__root__.keys()

    def values(self):
        return self._data.__root__.values()

    def items(self):
        return self._data.__root__.items()

    def __iter__(self):
        return iter(self._data.__root__)

    def __getitem__(self, key: str | int):
        return self._data.__root__[key]

    def __setitem__(self, key: str | int, value: BaseModel):
        self._data.__root__[key] = value

    def __delitem__(self, key: str | int):
        del self._data.__root__[key]

    def __len__(self):
        return len(self._data.__root__)
