from __future__ import annotations
from math import sqrt

from InformationRetrieval.Index.PostingList import PostingList
from InformationRetrieval.Index.PostingSkip import PostingSkip


class PostingSkipList(PostingList):

    _skipped: bool = False

    def __init__(self):
        super().__init__()

    def add(self, docId: int):
        p = PostingSkip(docId)
        last: PostingSkip = self.postings[len(self.postings) - 1]
        last.setNext(p)
        self.postings.append(p)

    def addSkipPointers(self):
        N = int(sqrt(self.size()))
        if not self._skipped:
            self._skipped = True
            i = 0
            posting = 0
            while posting != len(self.postings):
                if i % N == 0 and i + N < self.size():
                    j = 0
                    skip = posting
                    while j < N:
                        j = j + 1
                        skip = skip + 1
                    current: PostingSkip = self.postings[posting]
                    current.addSkip(self.postings[skip])
                posting = posting + 1
                i = i + 1

    def intersection(self, secondList: PostingSkipList):
        p1: PostingSkip = self.postings[0]
        p2: PostingSkip = secondList.postings[0]
        result = PostingSkipList()
        while p1 is not None and p2 is not None:
            if p1.getId() == p2.getId():
                result.add(p1.getId())
                p1 = p1.next()
                p2 = p2.next()
            else:
                if p1.getId() < p2.getId():
                    if self._skipped and p1.hasSkip() and p1.getSkip().getId() < p2.getId():
                        while p1.hasSkip() and p1.getSkip().getId() < p2.getId():
                            p1 = p1.getSkip()
                    else:
                        p1 = p1.next()
                else:
                    if self._skipped and p2.hasSkip() and p2.getSkip().getId() < p1.getId():
                        while p2.hasSkip() and p2.getSkip().getId() < p1.getId():
                            p2 = p2.getSkip()
                    else:
                        p2 = p2.next()
        return result
