from MorphologicalAnalysis.FsmMorphologicalAnalyzer cimport FsmMorphologicalAnalyzer
from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator

cdef class Parameter:

    cdef object _indexType
    cdef object _wordComparator
    cdef bint _loadIndexesFromFile
    cdef MorphologicalDisambiguator _disambiguator
    cdef FsmMorphologicalAnalyzer _fsm
    cdef bint _normalizeDocument
    cdef bint _phraseIndex
    cdef bint _positionalIndex
    cdef bint _constructNGramIndex
    cdef bint _constructIndexInDisk
    cdef bint _constructDictionaryInDisk
    cdef bint _limitNumberOfDocumentsLoaded
    cdef int _documentLimit
    cdef int _wordLimit

    cpdef object getIndexType(self)
    cpdef object getWordComparator(self)
    cpdef bint loadIndexesFromFile(self)
    cpdef MorphologicalDisambiguator getDisambiguator(self)
    cpdef FsmMorphologicalAnalyzer getFsm(self)
    cpdef bint constructPhraseIndex(self)
    cpdef bint normalizeDocument(self)
    cpdef bint constructPositionalIndex(self)
    cpdef bint constructNGramIndex(self)
    cpdef bint constructIndexInDisk(self)
    cpdef bint limitNumberOfDocumentsLoaded(self)
    cpdef int getDocumentLimit(self)
    cpdef bint constructDictionaryInDisk(self)
    cpdef int getWordLimit(self)
    cpdef setIndexType(self, object indexType)
    cpdef setWordComparator(self, object wordComparator)
    cpdef setLoadIndexesFromFile(self, bint loadIndexesFromFile)
    cpdef setDisambiguator(self, MorphologicalDisambiguator disambiguator)
    cpdef setFsm(self, FsmMorphologicalAnalyzer fsm)
    cpdef setNormalizeDocument(self, bint normalizeDocument)
    cpdef setPhraseIndex(self, bint phraseIndex)
    cpdef setPositionalIndex(self, bint positionalIndex)
    cpdef setNGramIndex(self, bint nGramIndex)
    cpdef setConstructIndexInDisk(self, bint constructIndexInDisk)
    cpdef setLimitNumberOfDocumentsLoaded(self, bint limitNumberOfDocumentsLoaded)
    cpdef setDocumentLimit(self, int documentLimit)
    cpdef setConstructDictionaryInDisk(self, bint constructDictionaryInDisk)
    cpdef setWordLimit(self, int wordLimit)
