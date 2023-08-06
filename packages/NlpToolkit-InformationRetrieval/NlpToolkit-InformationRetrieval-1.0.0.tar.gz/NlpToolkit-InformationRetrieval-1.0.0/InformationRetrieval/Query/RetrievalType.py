from enum import Enum, auto


class RetrievalType(Enum):
    BOOLEAN = auto()
    POSITIONAL = auto()
    RANKED = auto()
