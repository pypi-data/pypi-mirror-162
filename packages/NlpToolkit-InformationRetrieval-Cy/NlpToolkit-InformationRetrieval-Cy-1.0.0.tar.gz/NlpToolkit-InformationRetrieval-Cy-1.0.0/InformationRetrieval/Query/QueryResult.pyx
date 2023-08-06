from functools import cmp_to_key

from InformationRetrieval.Query.QueryResultItem cimport QueryResultItem

cdef class QueryResult:

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

    cpdef add(self, int docId, float score = 0.0):
        self._items.append(QueryResultItem(docId, score))

    cpdef list getItems(self):
        return self._items

    cpdef sort(self):
        self._items.sort(key=cmp_to_key(self.queryResultItemComparator))
