from Dictionary.Word import Word


class Query:

    _terms: [Word]

    def __init__(self, query: str):
        self._terms = []
        terms = query.split(" ")
        for term in terms:
            self._terms.append(Word(term))

    def getTerm(self, index: int) -> Word:
        return self._terms[index]

    def size(self) -> int:
        return len(self._terms)
