from InformationRetrieval.Index.PostingList cimport PostingList

cdef class PostingSkipList(PostingList):

    cdef bint _skipped

    cpdef add(self, int docId)
    cpdef addSkipPointers(self)
    cpdef PostingList intersection(self, PostingList secondList)
