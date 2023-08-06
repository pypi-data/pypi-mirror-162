cdef class QueryResultItem:

    def __init__(self, docId: int, score: float):
        self._docId = docId
        self._score = score

    cpdef int getDocId(self):
        return self._docId

    cpdef float getScore(self):
        return self._score
