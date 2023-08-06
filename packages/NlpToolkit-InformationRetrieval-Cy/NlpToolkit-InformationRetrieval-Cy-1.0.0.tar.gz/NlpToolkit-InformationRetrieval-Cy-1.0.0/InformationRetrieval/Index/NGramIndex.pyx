from InformationRetrieval.Index.TermOccurrence cimport TermOccurrence

cdef class NGramIndex(InvertedIndex):

    def __init__(self,
                 dictionaryOrfileName: object = None,
                 terms: [TermOccurrence] = None):
        super().__init__(dictionaryOrfileName, terms)
