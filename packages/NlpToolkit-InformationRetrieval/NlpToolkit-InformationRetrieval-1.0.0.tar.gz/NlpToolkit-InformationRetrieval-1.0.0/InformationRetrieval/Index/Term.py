from Dictionary.Word import Word


class Term(Word):

    _termId: int

    def __init__(self, name: str, termId: int):
        super().__init__(name)
        self._termId = termId

    def getTermId(self) -> int:
        return self._termId
