from Dictionary.Word cimport Word

cdef class Query:

    def __init__(self, query: str):
        self._terms = []
        terms = query.split(" ")
        for term in terms:
            self._terms.append(Word(term))

    cpdef Word getTerm(self, int index):
        return self._terms[index]

    cpdef int size(self):
        return len(self._terms)
