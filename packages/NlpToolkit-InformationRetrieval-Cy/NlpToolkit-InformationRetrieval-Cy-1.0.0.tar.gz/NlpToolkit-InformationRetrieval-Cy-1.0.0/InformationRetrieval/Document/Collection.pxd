from InformationRetrieval.Document.Parameter cimport Parameter
from InformationRetrieval.Index.IncidenceMatrix cimport IncidenceMatrix
from InformationRetrieval.Index.InvertedIndex cimport InvertedIndex
from InformationRetrieval.Index.NGramIndex cimport NGramIndex
from InformationRetrieval.Index.PositionalIndex cimport PositionalIndex
from InformationRetrieval.Index.TermDictionary cimport TermDictionary
from InformationRetrieval.Query.Query cimport Query

cdef class Collection:

    cdef object _indexType
    cdef TermDictionary _dictionary
    cdef TermDictionary _phraseDictionary
    cdef TermDictionary _biGramDictionary
    cdef TermDictionary _triGramDictionary
    cdef list _documents
    cdef IncidenceMatrix _incidenceMatrix
    cdef InvertedIndex _invertedIndex
    cdef NGramIndex _biGramIndex
    cdef NGramIndex _triGramIndex
    cdef PositionalIndex _positionalIndex
    cdef InvertedIndex _phraseIndex
    cdef PositionalIndex _phrasePositionalIndex
    cdef object _comparator
    cdef str _name
    cdef Parameter _parameter

    cpdef int size(self)
    cpdef int vocabularySize(self)
    cpdef save(self)
    cpdef constructDictionaryInDisk(self)
    cpdef constructIndexesInDisk(self)
    cpdef constructIndexesInMemory(self)
    cpdef list constructTerms(self, object termType)
    cpdef set constructDistinctWordList(self, object termType)
    cpdef bint notCombinedAllIndexes(self, list currentIdList)
    cpdef bint notCombinedAllDictionaries(self, list currentWords)
    cpdef list selectIndexesWithMinimumTermIds(self, list currentIdList)
    cpdef list selectDictionariesWithMinimumWords(self, list currentWords)
    cpdef combineMultipleDictionariesInDisk(self,
                                          str name,
                                          str tmpName,
                                          int blockCount)
    cpdef addNGramsToDictionaryAndIndex(self,
                                      str line,
                                      int k,
                                      TermDictionary nGramDictionary,
                                      NGramIndex nGramIndex)
    cpdef constructNGramDictionaryAndIndexInDisk(self)
    cpdef combineMultipleInvertedIndexesInDisk(self,
                                             str name,
                                             str tmpName,
                                             int blockCount)
    cpdef constructInvertedIndexInDisk(self,
                                     TermDictionary dictionary,
                                     object termType)
    cpdef constructDictionaryAndInvertedIndexInDisk(self, object termType)
    cpdef combineMultiplePositionalIndexesInDisk(self, str name, int blockCount)
    cpdef constructDictionaryAndPositionalIndexInDisk(self, object termType)
    cpdef constructPositionalIndexInDisk(self, TermDictionary dictionary, object termType)
    cpdef constructNGramIndex(self)
    cpdef searchCollection(self,
                         Query query,
                         object retrievalType,
                         object termWeighting,
                         object documentWeighting)
