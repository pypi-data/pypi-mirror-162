from InformationRetrieval.Index.TermDictionary cimport TermDictionary
from InformationRetrieval.Query.Query cimport Query
from InformationRetrieval.Query.QueryResult cimport QueryResult

cdef class IncidenceMatrix:

    cdef list _incidenceMatrix
    cdef int _dictionarySize
    cdef int _documentSize

    cpdef set(self, int row, int col)
    cpdef QueryResult search(self, Query query, TermDictionary dictionary)
