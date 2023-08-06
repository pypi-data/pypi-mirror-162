from InformationRetrieval.Index.TermDictionary cimport TermDictionary
from InformationRetrieval.Query.Query cimport Query
from InformationRetrieval.Query.QueryResult cimport QueryResult

cdef class InvertedIndex:

    cdef object _index

    cpdef readPostingList(self, str fileName)
    cpdef saveSorted(self, str fileName)
    cpdef save(self, str fileName)
    cpdef add(self, int termId, int docId)
    cpdef QueryResult search(self, Query query, TermDictionary dictionary)
