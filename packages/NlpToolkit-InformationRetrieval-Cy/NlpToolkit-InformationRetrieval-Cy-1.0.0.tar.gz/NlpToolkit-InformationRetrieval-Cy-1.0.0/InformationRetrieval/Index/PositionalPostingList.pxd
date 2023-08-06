from InformationRetrieval.Index.PositionalPosting cimport PositionalPosting
from InformationRetrieval.Query.QueryResult cimport QueryResult

cdef class PositionalPostingList:

    cdef list _postings

    cpdef int size(self)
    cpdef int getIndex(self, int docId)
    cpdef QueryResult toQueryResult(self)
    cpdef add(self, int docId, int position)
    cpdef PositionalPosting get(self, int index)
    cpdef PositionalPostingList union(self, PositionalPostingList secondList)
    cpdef PositionalPostingList intersection(self, PositionalPostingList secondList)
    cpdef writeToFile(self, object outfile, int index)
