from pathlib import Path
from typing import Type, cast

from filelock import SoftFileLock
from pydantic import BaseModel

from .data import DataMode, PydandyData
from .types import PydandyLock, PydandySource


class PydandyDB:
    def __init__(
        self,
        data_source: PydandySource = None,
    ) -> None:
        self._data = PydandyData()

        self.data_source = Path(data_source) if data_source is not None else None

        self.mode = self._set_mode()
        if self.mode != DataMode.IN_MEMORY and self.data_source is not None:
            self._lock: PydandyLock = SoftFileLock(self.data_source / ".lock")
        else:
            # Fake Lock for consistent behavior/types
            self._lock: PydandyLock = SoftFileLock("/tmp/pydandy.lock")

    def __getattribute__(self, __name: str):
        _data = super().__getattribute__("_data") or {}
        if __name in _data:
            _data = cast(PydandyData, _data)
            return _data.get_table(__name)
        else:
            return super().__getattribute__(__name)

    def _set_mode(self) -> DataMode:
        if self.data_source is None:
            return DataMode.IN_MEMORY

        elif not self.data_source.exists():
            if self.data_source.suffix == ".json":
                self.data_source.parent.mkdir(parents=True, exist_ok=True)
                with open(self.data_source, "w+") as f:
                    f.write(self._data.json(sort_keys=True, indent=4))
                return DataMode.FILE

            if self.data_source.suffix == "":
                self.data_source.mkdir(parents=True, exist_ok=True)
                return DataMode.DIRECTORY

        elif self.data_source.is_file() and self.data_source.suffix == ".json":
            return DataMode.FILE

        elif self.data_source.is_dir():
            return DataMode.DIRECTORY

        raise ValueError("Invalid data source. Must be a directory, JSON file, or None")

    def add_model(self, model: Type[BaseModel], name: str = None) -> None:
        self._data.add_model(model, name)

    def register(self, name: str = None):
        def _register(model: Type[BaseModel]):
            self._data.add_model(model, name)
            return model

        return _register
