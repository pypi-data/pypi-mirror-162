from Dictionary.Word cimport Word

cdef class Term(Word):

    cdef int _termId

    cpdef int getTermId(self)
