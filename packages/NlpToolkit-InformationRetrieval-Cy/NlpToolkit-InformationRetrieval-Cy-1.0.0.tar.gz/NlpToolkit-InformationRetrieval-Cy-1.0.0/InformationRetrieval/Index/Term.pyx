from Dictionary.Word cimport Word

cdef class Term(Word):

    def __init__(self, name: str, termId: int):
        super().__init__(name)
        self._termId = termId

    cpdef int getTermId(self):
        return self._termId
