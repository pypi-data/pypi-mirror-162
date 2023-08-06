from Corpus.Corpus cimport Corpus
from Corpus.Sentence cimport Sentence
from Corpus.SentenceSplitter cimport SentenceSplitter
from Dictionary.Word cimport Word

from InformationRetrieval.Index.TermOccurrence cimport TermOccurrence
from InformationRetrieval.Index.TermType import TermType

cdef class DocumentText(Corpus):

    def __init__(self, fileName: str, sentenceSplitter: SentenceSplitter = None):
        super().__init__(fileName, sentenceSplitter)

    cpdef set constructDistinctWordList(self, object termType):
        cdef set words
        cdef int i, j
        cdef Sentence sentence
        words = set()
        for i in range(self.sentenceCount()):
            sentence = self.getSentence(i)
            for j in range(sentence.wordCount()):
                if termType == TermType.TOKEN:
                    words.add(sentence.getWord(j).getName())
                elif termType == TermType.PHRASE:
                    if j < sentence.wordCount() - 1:
                        words.add(sentence.getWord(j).getName() + " " + sentence.getWord(j + 1).getName())
        return words

    cpdef list constructTermList(self, int docId, object termType):
        cdef list terms
        cdef int size, i, j
        cdef Sentence sentence
        terms = []
        size = 0
        for i in range(self.sentenceCount()):
            sentence = self.getSentence(i)
            for j in range(sentence.wordCount()):
                if termType == TermType.TOKEN:
                    terms.append(TermOccurrence(sentence.getWord(j), docId, size))
                    size = size + 1
                elif termType == TermType.PHRASE:
                    if j < sentence.wordCount() - 1:
                        terms.append(TermOccurrence(Word(sentence.getWord(j).getName() + " " + sentence.getWord(j + 1).getName()), docId, size))
                        size = size + 1
        return terms
