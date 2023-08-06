cdef class QueryResultItem:

    cdef int _docId
    cdef float _score

    cpdef int getDocId(self)
    cpdef float getScore(self)
