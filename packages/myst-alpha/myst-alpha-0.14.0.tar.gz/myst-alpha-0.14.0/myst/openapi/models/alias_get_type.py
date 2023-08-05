from enum import Enum


class AliasGetType(str, Enum):
    PROJECT = "Project"
    NODE = "Node"

    def __str__(self) -> str:
        return str(self.value)
