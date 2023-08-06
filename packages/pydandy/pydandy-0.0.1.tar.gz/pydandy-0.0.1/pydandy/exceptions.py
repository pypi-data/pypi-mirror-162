class ExistingRecord(Exception):
    def __init__(
        self,
        msg: str = "A record already exists with the given ID",
        *args: object,
    ) -> None:
        super().__init__(msg, *args)


class NonexistentRecord(Exception):
    def __init__(
        self,
        msg: str = "No record exists with the given ID",
        *args: object,
    ) -> None:
        super().__init__(msg, *args)
