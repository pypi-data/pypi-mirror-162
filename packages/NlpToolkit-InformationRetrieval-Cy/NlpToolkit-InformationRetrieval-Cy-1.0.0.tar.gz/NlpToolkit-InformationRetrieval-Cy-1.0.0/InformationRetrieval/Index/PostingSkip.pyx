cdef class PostingSkip(Posting):

    def __init__(self, Id: int):
        super().__init__(Id)
        self._skipAvailable = False
        self._skip = None
        self._next = None

    cpdef bint hasSkip(self):
        return self._skipAvailable

    cpdef addSkip(self, PostingSkip skip):
        self._skipAvailable = True
        self._skip = skip

    cpdef setNext(self, PostingSkip _next):
        self._next = _next

    cpdef PostingSkip next(self):
        return self._next

    cpdef PostingSkip getSkip(self):
        return self._skip
