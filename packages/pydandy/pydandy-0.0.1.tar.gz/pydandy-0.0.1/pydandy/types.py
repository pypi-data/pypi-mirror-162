from __future__ import annotations

from pathlib import Path
from typing import Hashable

from filelock import SoftFileLock
from pydantic import BaseModel

PydandyLock = SoftFileLock
PydandySource = Path | str | None

PydandyTable = dict[Hashable, BaseModel]
