from Dictionary.Word cimport Word

cdef class TermOccurrence:

    cdef Word _term
    cdef int _docID
    cdef int _position

    cpdef Word getTerm(self)
    cpdef int getDocId(self)
    cpdef int getPosition(self)
    cpdef bint isDifferent(self, TermOccurrence currentTerm)
