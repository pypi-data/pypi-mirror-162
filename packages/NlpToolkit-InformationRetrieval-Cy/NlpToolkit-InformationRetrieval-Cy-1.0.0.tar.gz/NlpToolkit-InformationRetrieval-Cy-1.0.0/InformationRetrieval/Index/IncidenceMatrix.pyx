from InformationRetrieval.Index.TermOccurrence cimport TermOccurrence

cdef class IncidenceMatrix:

    def __init__(self, terms: [TermOccurrence], dictionary: TermDictionary, documentSize: int):
        cdef int i
        cdef TermOccurrence term
        self._dictionarySize = dictionary.size()
        self._documentSize = documentSize
        self._incidenceMatrix = [[False for _ in range(self._documentSize)] for _ in range(self._dictionarySize)]
        if len(terms) > 0:
            term = terms[0]
            i = 1
            self.set(dictionary.getWordIndex(term.getTerm().getName()), term.getDocId())
            while i < len(terms):
                term = terms[i]
                self.set(dictionary.getWordIndex(term.getTerm().getName()), term.getDocId())
                i = i + 1

    cpdef set(self, int row, int col):
        self._incidenceMatrix[row][col] = True

    cpdef QueryResult search(self, Query query, TermDictionary dictionary):
        cdef QueryResult result
        cdef list resultRow
        cdef int i, j, termIndex
        result = QueryResult()
        resultRow = [True for _ in range(self._documentSize)]
        for i in range(query.size()):
            termIndex = dictionary.getWordIndex(query.getTerm(i).getName())
            if termIndex != -1:
                for j in range(self._documentSize):
                    resultRow[j] = resultRow[j] and self._incidenceMatrix[termIndex][j]
        for i in range(self._documentSize):
            if resultRow[i]:
                result.add(i)
        return result
