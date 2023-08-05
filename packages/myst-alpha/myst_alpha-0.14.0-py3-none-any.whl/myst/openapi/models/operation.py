from enum import Enum


class Operation(str, Enum):
    VIEW = "VIEW"
    EDIT = "EDIT"
    RESHARE = "RESHARE"
    TRANSFER_OWNERSHIP = "TRANSFER_OWNERSHIP"
    DELETE = "DELETE"

    def __str__(self) -> str:
        return str(self.value)
