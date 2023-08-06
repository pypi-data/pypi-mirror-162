from Corpus.Corpus cimport Corpus
from MorphologicalAnalysis.FsmMorphologicalAnalyzer cimport FsmMorphologicalAnalyzer
from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator

from InformationRetrieval.Document.DocumentText cimport DocumentText

cdef class Document:

    cdef str _absoluteFileName
    cdef str _fileName
    cdef int _docId
    cdef int _size

    cpdef DocumentText loadDocument(self)
    cpdef Corpus normalizeDocument(self,
                          MorphologicalDisambiguator disambiguator,
                          FsmMorphologicalAnalyzer fsm)
    cpdef int getDocId(self)
    cpdef str getFileName(self)
    cpdef str getAbsoluteFileName(self)
    cpdef int getSize(self)
