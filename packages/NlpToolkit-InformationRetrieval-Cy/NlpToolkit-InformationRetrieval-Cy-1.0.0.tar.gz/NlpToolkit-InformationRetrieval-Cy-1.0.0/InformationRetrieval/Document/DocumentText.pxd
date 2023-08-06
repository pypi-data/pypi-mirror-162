from Corpus.Corpus cimport Corpus

cdef class DocumentText(Corpus):

    cpdef set constructDistinctWordList(self, object termType)
    cpdef list constructTermList(self, int docId, object termType)
