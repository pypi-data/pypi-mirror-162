from __future__ import annotations

from InformationRetrieval.Index.Posting import Posting


class PostingSkip(Posting):

    _skipAvailable: bool = False
    _skip: PostingSkip = None
    _next: PostingSkip = None

    def __init__(self, Id: int):
        super().__init__(Id)

    def hasSkip(self) -> bool:
        return self._skipAvailable

    def addSkip(self, skip: PostingSkip):
        self._skipAvailable = True
        self._skip = skip

    def setNext(self, _next: PostingSkip):
        self._next = _next

    def next(self) -> PostingSkip:
        return self._next

    def getSkip(self) -> PostingSkip:
        return self._skip
