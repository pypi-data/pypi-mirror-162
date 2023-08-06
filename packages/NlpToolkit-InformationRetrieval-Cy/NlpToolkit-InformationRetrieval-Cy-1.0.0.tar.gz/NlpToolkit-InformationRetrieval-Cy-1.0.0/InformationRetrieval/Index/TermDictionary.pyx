from functools import cmp_to_key

from Dictionary.Dictionary cimport Dictionary
from Dictionary.Word cimport Word

from InformationRetrieval.Index.Term cimport Term
from InformationRetrieval.Index.TermOccurrence cimport TermOccurrence

cdef class TermDictionary(Dictionary):

    def __init__(self, comparator: object, fileNameOrTerms = None):
        cdef str fileName, line, word
        cdef int termId
        cdef list terms
        cdef TermOccurrence term, previousTerm
        cdef int i
        cdef list wordList
        cdef Word termWord
        super().__init__(comparator)
        if fileNameOrTerms is not None:
            if isinstance(fileNameOrTerms, str):
                fileName = fileNameOrTerms
                infile = open(fileName + "-dictionary.txt", mode='r', encoding='utf-8')
                line = infile.readline().strip()
                while line != "":
                    termId = int(line[0:line.index(" ")])
                    self.words.append(Term(line[line.index(" ") + 1:], termId))
                    line = infile.readline().strip()
                infile.close()
            else:
                if isinstance(fileNameOrTerms, list):
                    termId = 0
                    terms = fileNameOrTerms
                    if len(terms) > 0:
                        term = terms[0]
                        self.addTerm(term.getTerm().getName(), termId)
                        termId = termId + 1
                        previousTerm = term
                        i = 1
                        while i < len(terms):
                            term = terms[i]
                            if term.isDifferent(previousTerm):
                                self.addTerm(term.getTerm().getName(), termId)
                                termId = termId + 1
                            i = i + 1
                            previousTerm = term
                else:
                    wordList = []
                    for word in fileNameOrTerms:
                        wordList.append(Word(word))
                    wordList.sort(key=cmp_to_key(comparator))
                    termId = 0
                    for termWord in wordList:
                        self.addTerm(termWord.getName(), termId)
                        termId = termId + 1

    cpdef int __getPosition(self, Word word):
        cdef int lo, hi, mid
        lo = 0
        hi = len(self.words) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.comparator(self.words[mid], word) < 0:
                lo = mid + 1
            elif self.comparator(self.words[mid], word) > 0:
                hi = mid - 1
            else:
                return mid
        return -(lo + 1)

    cpdef addTerm(self, str name, int termId):
        cdef int middle
        middle = self.__getPosition(Word(name))
        if middle < 0:
            self.words.insert(-middle - 1, Term(name, termId))

    cpdef save(self, str fileName):
        cdef Word word
        cdef Term term
        outfile = open(fileName + "-dictionary.txt", mode='w', encoding='utf-8')
        for word in self.words:
            term = word
            outfile.write(term.getTermId().__str__() + " " + term.getName() + "\n")
        outfile.close()

    @staticmethod
    def constructNGrams(word: str, termId: int, k: int) -> [TermOccurrence]:
        cdef list nGrams
        cdef int j
        cdef str term
        nGrams = []
        if len(word) >= k - 1:
            for j in range(-1, len(word) - k + 2):
                if j == -1:
                    term = "$" + word[0:k - 1]
                elif j == len(word) - k + 1:
                    term = word[j: j + k - 1] + "$"
                else:
                    term = word[j: j + k]
                nGrams.append(TermOccurrence(Word(term), termId, j))
        return nGrams

    cpdef list constructTermsFromDictionary(self, int k):
        cdef list terms
        cdef int i
        cdef str word
        terms = []
        for i in range(self.size()):
            word = self.getWordWithIndex(i).getName()
            terms.extend(TermDictionary.constructNGrams(word, i, k))
        terms.sort(key=cmp_to_key(TermOccurrence.termOccurrenceComparator))
        return terms
