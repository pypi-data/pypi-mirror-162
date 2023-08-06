class QueryResultItem:

    _docId: int
    _score: float

    def __init__(self, docId: int, score: float):
        self._docId = docId
        self._score = score

    def getDocId(self) -> int:
        return self._docId

    def getScore(self) -> float:
        return self._score
