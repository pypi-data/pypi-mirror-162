cdef class PositionalPosting(Posting):

    def __init__(self, docId: int):
        self._positions = []
        self._docId = docId

    cpdef add(self, int position):
        self._positions.append(Posting(position))

    cpdef int getDocId(self):
        return self._docId

    cpdef list getPositions(self):
        return self._positions

    cpdef int size(self):
        return len(self._positions)

    def __str__(self) -> str:
        cdef str result
        cdef Posting posting
        result = self._docId.__str__() + " " + len(self._positions).__str__()
        for posting in self._positions:
            result = result + " " + posting.getId().__str__()
        return result
