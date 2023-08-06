from Dictionary.Dictionary cimport Dictionary
from Dictionary.Word cimport Word

cdef class TermDictionary(Dictionary):

    cpdef int __getPosition(self, Word word)
    cpdef addTerm(self, str name, int termId)
    cpdef save(self, str fileName)
    cpdef list constructTermsFromDictionary(self, int k)
