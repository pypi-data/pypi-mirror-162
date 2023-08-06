from Corpus.Corpus cimport Corpus
from Corpus.Sentence cimport Sentence
from Corpus.TurkishSplitter cimport TurkishSplitter
from Dictionary.Word cimport Word
from MorphologicalAnalysis.FsmMorphologicalAnalyzer cimport FsmMorphologicalAnalyzer
from MorphologicalAnalysis.FsmParse cimport FsmParse
from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator

cdef class Document:

    def __init__(self, absoluteFileName: str, fileName: str, docId: int):
        self._size = 0
        self._absoluteFileName = absoluteFileName
        self._fileName = fileName
        self._docId = docId

    cpdef DocumentText loadDocument(self):
        documentText = DocumentText(self._absoluteFileName, TurkishSplitter())
        self._size = documentText.numberOfWords()
        return documentText

    cpdef Corpus normalizeDocument(self,
                                   MorphologicalDisambiguator disambiguator,
                                   FsmMorphologicalAnalyzer fsm):
        cdef Corpus corpus
        cdef int i
        cdef Sentence sentence, newSentence
        cdef FsmParse fsmParse
        corpus = Corpus(self._absoluteFileName)
        for i in range(corpus.sentenceCount()):
            sentence = corpus.getSentence(i)
            parses = fsm.robustMorphologicalAnalysis(sentence)
            correctParses = disambiguator.disambiguate(parses)
            newSentence = Sentence()
            for fsmParse in correctParses:
                newSentence.addWord(Word(fsmParse.getWord().getName()))
            corpus.addSentence(newSentence)
        self._size = corpus.numberOfWords()
        return corpus

    cpdef int getDocId(self):
        return self._docId

    cpdef str getFileName(self):
        return self._fileName

    cpdef str getAbsoluteFileName(self):
        return self._absoluteFileName

    cpdef int getSize(self):
        return self._size
