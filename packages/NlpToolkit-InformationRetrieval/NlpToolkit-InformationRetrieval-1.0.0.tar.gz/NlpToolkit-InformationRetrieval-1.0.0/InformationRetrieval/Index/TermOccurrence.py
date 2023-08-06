from __future__ import annotations

from Dictionary.Word import Word


class TermOccurrence:

    _term: Word
    _docID: int
    _position: int

    def __init__(self, term: Word, docID: int, position: int):
        self._term = term
        self._docID = docID
        self._position = position

    @staticmethod
    def ignoreCaseComparator(wordA: Word, wordB: Word):
        IGNORE_CASE_LETTERS = "aAbBcCçÇdDeEfFgGğĞhHıIiİjJkKlLmMnNoOöÖpPqQrRsSşŞtTuUüÜvVwWxXyYzZ"
        for i in range(min(len(wordA.getName()), len(wordB.getName()))):
            firstChar = wordA.getName()[i:i + 1]
            secondChar = wordB.getName()[i:i + 1]
            if firstChar != secondChar:
                if firstChar in IGNORE_CASE_LETTERS and secondChar not in IGNORE_CASE_LETTERS:
                    return -1
                elif firstChar not in IGNORE_CASE_LETTERS and secondChar in IGNORE_CASE_LETTERS:
                    return 1
                elif firstChar in IGNORE_CASE_LETTERS and secondChar in IGNORE_CASE_LETTERS:
                    first = IGNORE_CASE_LETTERS.index(firstChar)
                    second = IGNORE_CASE_LETTERS.index(secondChar)
                    if first < second:
                        return -1
                    elif first > second:
                        return 1
                else:
                    if firstChar < secondChar:
                        return -1
                    else:
                        return 1
        if len(wordA.getName()) < len(wordB.getName()):
            return -1
        elif len(wordA.getName()) > len(wordB.getName()):
            return 1
        else:
            return 0

    @staticmethod
    def termOccurrenceComparator(termA: TermOccurrence, termB: TermOccurrence):
        if termA.getTerm().getName() != termB.getTerm().getName():
            return TermOccurrence.ignoreCaseComparator(termA.getTerm(), termB.getTerm())
        elif termA.getDocId() == termB.getDocId():
            if termA.getPosition() == termB.getPosition():
                return 0
            elif termA.getPosition() < termB.getPosition():
                return -1
            else:
                return 1
        elif termA.getDocId() < termB.getDocId():
            return -1
        else:
            return 1

    def getTerm(self) -> Word:
        return self._term

    def getDocId(self) -> int:
        return self._docID

    def getPosition(self) -> int:
        return self._position

    def isDifferent(self, currentTerm: TermOccurrence) -> bool:
        return self._term.getName() != currentTerm.getTerm().getName()
