from InformationRetrieval.Index.TermDictionary import TermDictionary
from InformationRetrieval.Index.TermOccurrence import TermOccurrence
from InformationRetrieval.Query.Query import Query
from InformationRetrieval.Query.QueryResult import QueryResult


class IncidenceMatrix:

    _incidenceMatrix: [[bool]]
    _dictionarySize: int
    _documentSize: int

    def __init__(self, terms: [TermOccurrence], dictionary: TermDictionary, documentSize: int):
        self._dictionarySize = dictionary.size()
        self._documentSize = documentSize
        self._incidenceMatrix = [[False for _ in range(self._documentSize)] for _ in range(self._dictionarySize)]
        if len(terms) > 0:
            term: TermOccurrence = terms[0]
            i = 1
            self.set(dictionary.getWordIndex(term.getTerm().getName()), term.getDocID())
            while i < len(terms):
                term = terms[i]
                self.set(dictionary.getWordIndex(term.getTerm().getName()), term.getDocID())
                i = i + 1

    def set(self, row: int, col: int):
        self._incidenceMatrix[row][col] = True

    def search(self, query: Query, dictionary: TermDictionary) -> QueryResult:
        result = QueryResult()
        resultRow = [True for _ in range(self._documentSize)]
        for i in range(query.size()):
            termIndex = dictionary.getWordIndex(query.getTerm(i).getName())
            if termIndex != -1:
                for j in range(self._documentSize):
                    resultRow[j] = resultRow[j] and self._incidenceMatrix[termIndex][j]
        for i in range(self._documentSize):
            if resultRow[i]:
                result.add(i)
        return result
