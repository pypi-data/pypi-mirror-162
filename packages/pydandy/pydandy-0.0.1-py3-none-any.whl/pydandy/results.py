from pydantic import BaseModel


class PydandyResults(BaseModel):
    records: list[BaseModel]
