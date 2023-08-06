from functools import cmp_to_key

from InformationRetrieval.Query.QueryResultItem import QueryResultItem


class QueryResult:

    _items: [QueryResultItem]

    @staticmethod
    def queryResultItemComparator(resultA: QueryResultItem, resultB: QueryResultItem):
        if resultA.getScore() > resultB.getScore():
            return -1
        else:
            if resultA.getScore() < resultB.getScore():
                return 1
            else:
                return 0

    def __init__(self):
        self._items = []

    def add(self, docId: int, score: float = 0.0):
        self._items.append(QueryResultItem(docId, score))

    def getItems(self) -> [QueryResultItem]:
        return self._items

    def sort(self):
        self._items.sort(key=cmp_to_key(self.queryResultItemComparator))
