from enum import Enum, auto


class DocumentWeighting(Enum):
    NO_IDF = auto(),
    IDF = auto(),
    PROBABILISTIC_IDF = auto()
