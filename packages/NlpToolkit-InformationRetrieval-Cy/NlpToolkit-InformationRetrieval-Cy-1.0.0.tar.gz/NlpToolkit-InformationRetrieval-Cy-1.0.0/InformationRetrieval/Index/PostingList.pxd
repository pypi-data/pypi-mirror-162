from InformationRetrieval.Query.QueryResult cimport QueryResult

cdef class PostingList:

    cdef list _postings

    cpdef add(self, int docId)
    cpdef int size(self)
    cpdef PostingList intersection(self, PostingList secondList)
    cpdef PostingList union(self, PostingList secondList)
    cpdef QueryResult toQueryResult(self)
    cpdef writeToFile(self, object outfile, int index)
