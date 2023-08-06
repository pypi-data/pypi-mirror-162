cdef class VectorSpaceModel:

    cdef list _model

    cpdef float get(self, int index)
    cpdef cosineSimilarity(self, VectorSpaceModel secondModel)
