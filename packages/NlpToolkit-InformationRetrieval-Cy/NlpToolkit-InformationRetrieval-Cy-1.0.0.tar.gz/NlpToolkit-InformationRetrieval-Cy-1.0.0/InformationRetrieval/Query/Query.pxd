from Dictionary.Word cimport Word

cdef class Query:

    cdef list _terms

    cpdef Word getTerm(self, int index)
    cpdef int size(self)
