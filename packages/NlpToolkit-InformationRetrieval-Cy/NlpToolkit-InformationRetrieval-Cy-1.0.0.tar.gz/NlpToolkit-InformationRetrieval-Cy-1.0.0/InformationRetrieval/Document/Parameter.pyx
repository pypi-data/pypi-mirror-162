from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer
from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator

from InformationRetrieval.Document.IndexType import IndexType
from InformationRetrieval.Index.TermOccurrence import TermOccurrence

cdef class Parameter:

    def __init__(self):
        self._indexType = IndexType.INVERTED_INDEX
        self._loadIndexesFromFile = False
        self._normalizeDocument = False
        self._phraseIndex = True
        self._positionalIndex = True
        self._constructNGramIndex = True
        self._constructIndexInDisk = False
        self._constructDictionaryInDisk = False
        self._limitNumberOfDocumentsLoaded = False
        self._documentLimit = 1000
        self._wordLimit = 10000
        self._wordComparator = TermOccurrence.ignoreCaseComparator

    cpdef object getIndexType(self):
        return self._indexType

    cpdef object getWordComparator(self):
        return self._wordComparator

    cpdef bint loadIndexesFromFile(self):
        return self._loadIndexesFromFile

    cpdef MorphologicalDisambiguator getDisambiguator(self):
        return self._disambiguator

    cpdef FsmMorphologicalAnalyzer getFsm(self):
        return self._fsm

    cpdef bint constructPhraseIndex(self):
        return self._phraseIndex

    cpdef bint normalizeDocument(self):
        return self._normalizeDocument

    cpdef bint constructPositionalIndex(self):
        return self._positionalIndex

    cpdef bint constructNGramIndex(self):
        return self._constructNGramIndex

    cpdef bint constructIndexInDisk(self):
        return self._constructIndexInDisk

    cpdef bint limitNumberOfDocumentsLoaded(self):
        return self._limitNumberOfDocumentsLoaded

    cpdef int getDocumentLimit(self):
        return self._documentLimit

    cpdef bint constructDictionaryInDisk(self):
        return self._constructDictionaryInDisk

    cpdef int getWordLimit(self):
        return self._wordLimit

    cpdef setIndexType(self, object indexType):
        self._indexType = indexType

    cpdef setWordComparator(self, object wordComparator):
        self._wordComparator = wordComparator

    cpdef setLoadIndexesFromFile(self, bint loadIndexesFromFile):
        self._loadIndexesFromFile = loadIndexesFromFile

    cpdef setDisambiguator(self, MorphologicalDisambiguator disambiguator):
        self._disambiguator = disambiguator

    cpdef setFsm(self, FsmMorphologicalAnalyzer fsm):
        self._fsm = fsm

    cpdef setNormalizeDocument(self, bint normalizeDocument):
        self._normalizeDocument = normalizeDocument

    cpdef setPhraseIndex(self, bint phraseIndex):
        self._phraseIndex = phraseIndex

    cpdef setPositionalIndex(self, bint positionalIndex):
        self._positionalIndex = positionalIndex

    cpdef setNGramIndex(self, bint nGramIndex):
        self._constructNGramIndex = nGramIndex

    cpdef setConstructIndexInDisk(self, bint constructIndexInDisk):
        self._constructIndexInDisk = constructIndexInDisk

    cpdef setLimitNumberOfDocumentsLoaded(self, bint limitNumberOfDocumentsLoaded):
        self._limitNumberOfDocumentsLoaded = limitNumberOfDocumentsLoaded

    cpdef setDocumentLimit(self, int documentLimit):
        self._documentLimit = documentLimit

    cpdef setConstructDictionaryInDisk(self, bint constructDictionaryInDisk):
        self._constructDictionaryInDisk = constructDictionaryInDisk
        if self._constructDictionaryInDisk:
            self._constructIndexInDisk = True

    cpdef setWordLimit(self, int wordLimit):
        self._wordLimit = wordLimit
