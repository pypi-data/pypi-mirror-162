from InformationRetrieval.Index.Posting cimport Posting

cdef class PositionalPosting(Posting):

    cdef list _positions
    cdef int _docId

    cpdef add(self, int position)
    cpdef int getDocId(self)
    cpdef list getPositions(self)
    cpdef int size(self)
