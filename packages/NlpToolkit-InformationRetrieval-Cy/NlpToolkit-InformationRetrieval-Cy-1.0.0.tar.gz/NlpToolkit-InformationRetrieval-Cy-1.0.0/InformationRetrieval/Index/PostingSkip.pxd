from InformationRetrieval.Index.Posting cimport Posting

cdef class PostingSkip(Posting):

    cdef bint _skipAvailable
    cdef PostingSkip _skip
    cdef PostingSkip _next

    cpdef bint hasSkip(self)
    cpdef addSkip(self, PostingSkip skip)
    cpdef setNext(self, PostingSkip _next)
    cpdef PostingSkip next(self)
    cpdef PostingSkip getSkip(self)
