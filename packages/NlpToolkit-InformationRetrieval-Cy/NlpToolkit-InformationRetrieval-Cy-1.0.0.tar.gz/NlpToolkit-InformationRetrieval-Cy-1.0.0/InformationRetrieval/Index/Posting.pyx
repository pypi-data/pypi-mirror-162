cdef class Posting:

    def __init__(self, Id: int):
        self.Id = Id

    cpdef int getId(self):
        return self.Id
