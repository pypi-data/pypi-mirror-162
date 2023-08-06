from __future__ import annotations
from io import TextIOWrapper
from typing import TextIO

from InformationRetrieval.Index.PositionalPosting import PositionalPosting
from InformationRetrieval.Query.QueryResult import QueryResult


class PositionalPostingList:

    _postings: [PositionalPosting]

    def __init__(self, infile: TextIO = None, count: int = None):
        self._postings = []
        if infile is not None:
            for i in range(count):
                line = infile.readline().strip()
                ids = line.split(" ")
                numberOfPositionalPostings = int(ids[1])
                if len(ids) == numberOfPositionalPostings + 2:
                    docId = int(ids[0])
                    for j in range(numberOfPositionalPostings):
                        positionalPosting = int(ids[j + 2])
                        self.add(docId, positionalPosting)

    def size(self) -> int:
        return len(self._postings)

    def getIndex(self, docId: int) -> int:
        begin = 0
        end = self.size() - 1
        while begin <= end:
            middle = (begin + end) // 2
            if docId == self._postings[middle].getDocId():
                return middle
            else:
                if docId == self._postings[middle].getDocId():
                    end = middle - 1
                else:
                    begin = middle + 1
        return -1

    def toQueryResult(self) -> QueryResult:
        result = QueryResult()
        for posting in self._postings:
            result.add(posting.getDocId())
        return result

    def add(self, docId: int, position: int):
        index = self.getIndex(docId)
        if index == -1:
            self._postings.append(PositionalPosting(docId))
            self._postings[len(self._postings) - 1].add(position)
        else:
            self._postings[index].add(position)

    def get(self, index: int) -> PositionalPosting:
        return self._postings[index]

    def union(self, secondList: PositionalPostingList) -> PositionalPostingList:
        result = PositionalPostingList()
        result._postings.extend(self._postings)
        result._postings.extend(secondList._postings)
        return result

    def intersection(self, secondList: PositionalPostingList) -> PositionalPostingList:
        i = 0
        j = 0
        result = PositionalPostingList()
        while i < len(self._postings) and j < len(secondList._postings):
            p1: PositionalPosting = self._postings[i]
            p2: PositionalPosting = secondList._postings[j]
            if p1.getDocId() == p2.getDocId():
                position1 = 0
                position2 = 0
                postings1 = p1.getPositions()
                postings2 = p2.getPositions()
                while position1 < len(postings1) and position2 < len(postings2):
                    if postings1[position1] + 1 == postings2[position2].getId():
                        result.add(p1.getDocId(), postings2[position2].getId())
                        position1 = position1 + 1
                        position2 = position2 + 1
                    else:
                        if postings1[position1].getId() + 1 < postings2[position2].getId():
                            position1 = position1 + 1
                        else:
                            position2 = position2 + 1
                i = i + 1
                j = j + 1
            else:
                if p1.getDocId() < p2.getDocId():
                    i = i + 1
                else:
                    j = j + 1
        return result

    def __str__(self) -> str:
        result = ""
        for positionalPosting in self._postings:
            result = result + "\t" + positionalPosting.__str__() + "\n"
        return result

    def writeToFile(self, outfile: TextIO, index: int):
        if self.size() > 0:
            outfile.write(index.__str__() + " " + self.size().__str__() + "\n")
            outfile.write(self.__str__())
