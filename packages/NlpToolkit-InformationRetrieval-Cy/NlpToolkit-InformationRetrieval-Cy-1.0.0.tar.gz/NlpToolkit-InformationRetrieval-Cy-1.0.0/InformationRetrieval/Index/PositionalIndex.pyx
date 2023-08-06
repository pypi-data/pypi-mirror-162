from collections import OrderedDict

from InformationRetrieval.Index.PositionalPosting cimport PositionalPosting
from InformationRetrieval.Index.PositionalPostingList cimport PositionalPostingList
from InformationRetrieval.Index.TermOccurrence cimport TermOccurrence
from InformationRetrieval.Query.VectorSpaceModel cimport VectorSpaceModel

cdef class PositionalIndex:

    def __init__(self,
                 dictionaryOrfileName: object = None,
                 terms: [TermOccurrence] = None):
        cdef TermDictionary dictionary
        cdef TermOccurrence term, previousTerm
        cdef int i, termId, prevDocId
        self._positionalIndex = OrderedDict()
        if dictionaryOrfileName is not None:
            if isinstance(dictionaryOrfileName, TermDictionary):
                dictionary = dictionaryOrfileName
                if len(terms) > 0:
                    term = terms[0]
                    i = 1
                    previousTerm = term
                    termId = dictionary.getWordIndex(term.getTerm().getName())
                    self.addPosition(termId, term.getDocId(), term.getPosition())
                    prevDocId = term.getDocId()
                    while i < len(terms):
                        term = terms[i]
                        termId = dictionary.getWordIndex(term.getTerm().getName())
                        if termId != -1:
                            if term.isDifferent(previousTerm):
                                self.addPosition(termId, term.getDocId(), term.getPosition())
                                prevDocId = term.getDocId()
                            elif prevDocId != term.getDocId():
                                self.addPosition(termId, term.getDocId(), term.getPosition())
                                prevDocId = term.getDocId()
                            else:
                                self.addPosition(termId, term.getDocId(), term.getPosition())
                        i = i + 1
                        previousTerm = term
            elif isinstance(dictionaryOrfileName, str):
                self.readPositionalPostingList(dictionaryOrfileName)

    cpdef readPositionalPostingList(self, str fileName):
        cdef str line
        cdef list items
        cdef int wordId
        infile = open(fileName + "-positionalPostings.txt", mode="r", encoding="utf-8")
        line = infile.readline().strip()
        while line != "":
            items = line.split(" ")
            wordId = int(items[0])
            self._positionalIndex[wordId] = PositionalPostingList(infile, int(items[1]))
            line = infile.readline().strip()
        infile.close()

    cpdef saveSorted(self, str fileName):
        cdef list items
        cdef int key
        items = []
        for key in self._positionalIndex.keys():
            items.append([key, self._positionalIndex[key]])
        items.sort()
        outfile = open(fileName + "-positionalPostings.txt", mode="w", encoding="utf-8")
        for item in items:
            item[1].writeToFile(outfile, item[0])
        outfile.close()

    cpdef save(self, str fileName):
        cdef int key
        outfile = open(fileName + "-positionalPostings.txt", mode="w", encoding="utf-8")
        for key in self._positionalIndex.keys():
            self._positionalIndex[key].writeToFile(outfile, key)
        outfile.close()

    cpdef addPosition(self, int termId, int docId, int position):
        cdef PositionalPostingList positionalPostingList
        if termId in self._positionalIndex:
            positionalPostingList = self._positionalIndex[termId]
        else:
            positionalPostingList = PositionalPostingList()
        positionalPostingList.add(docId, position)
        self._positionalIndex[termId] = positionalPostingList

    cpdef QueryResult positionalSearch(self, Query query, TermDictionary dictionary):
        cdef PositionalPostingList postingResult
        cdef int i, term
        postingResult  = None
        for i in range(query.size()):
            term = dictionary.getWordIndex(query.getTerm(i).getName())
            if term != -1:
                if i == 0:
                    postingResult = self._positionalIndex[term]
                elif postingResult is not None:
                    postingResult = postingResult.intersection(self._positionalIndex[term])
                else:
                    return None
            else:
                return None
        if postingResult is not None:
            return postingResult.toQueryResult()
        else:
            return None

    cpdef list getTermFrequencies(self, int docId):
        cdef list tf
        cdef int i, key, index
        cdef PositionalPostingList positionalPostingList
        tf = []
        i = 0
        for key in self._positionalIndex.keys():
            positionalPostingList = self._positionalIndex[key]
            index = positionalPostingList.getIndex(docId)
            if index != -1:
                tf.append(positionalPostingList.get(index).size())
            else:
                tf.append(0)
            i = i + 1
        return tf

    cpdef list getDocumentFrequencies(self):
        cdef list df
        cdef int i, key
        df = []
        i = 0
        for key in self._positionalIndex.keys():
            df.append(self._positionalIndex[key].size())
            i = i + 1
        return df

    cpdef QueryResult rankedSearch(self,
                     Query query,
                     TermDictionary dictionary,
                     list documents,
                     object termWeighting,
                     object documentWeighting):
        cdef int N, i, term, j, docId
        cdef float tf, df
        cdef QueryResult result
        cdef list scores
        cdef PositionalPostingList positionalPostingList
        cdef PositionalPosting positionalPosting
        N = len(documents)
        result = QueryResult()
        scores = [0 for _ in range(N)]
        for i in range(query.size()):
            term = dictionary.getWordIndex(query.getTerm(i).getName())
            if term != -1:
                positionalPostingList = self._positionalIndex[term]
                for j in range(positionalPostingList.size()):
                    positionalPosting = positionalPostingList.get(j)
                    docId = positionalPosting.getDocId()
                    tf = positionalPosting.size()
                    df = self._positionalIndex[term].size()
                    if tf > 0 and df > 0:
                        scores[docId] = scores[docId] + VectorSpaceModel.weighting(tf, df, N, termWeighting, documentWeighting)
        for i in range(N):
            scores[i] = scores[i] / documents[i].getSize()
            if scores[i] > 0:
                result.add(i, scores[i])
        result.sort()
        return result
