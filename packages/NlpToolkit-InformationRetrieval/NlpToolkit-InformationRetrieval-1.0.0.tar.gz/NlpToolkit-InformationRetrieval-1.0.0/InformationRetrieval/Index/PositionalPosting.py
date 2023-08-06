from InformationRetrieval.Index.Posting import Posting


class PositionalPosting:

    _positions: [Posting]
    _docId: int

    def __init__(self, docId: int):
        self._positions = []
        self._docId = docId

    def add(self, position: int):
        self._positions.append(Posting(position))

    def getDocId(self) -> int:
        return self._docId

    def getPositions(self) -> [Posting]:
        return self._positions

    def size(self) -> int:
        return len(self._positions)

    def __str__(self):
        result = self._docId.__str__() + " " + len(self._positions).__str__()
        for posting in self._positions:
            result = result + " " + posting.getId().__str__()
        return result
