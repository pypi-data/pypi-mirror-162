import os
from functools import cmp_to_key

from Dictionary.Word cimport Word

from InformationRetrieval.Document.Document cimport Document
from InformationRetrieval.Document.DocumentText cimport DocumentText
from InformationRetrieval.Document.IndexType import IndexType
from InformationRetrieval.Index.PositionalPostingList cimport PositionalPostingList
from InformationRetrieval.Index.PostingList cimport PostingList
from InformationRetrieval.Index.TermOccurrence cimport TermOccurrence
from InformationRetrieval.Index.TermType import TermType
from InformationRetrieval.Query.RetrievalType import RetrievalType

cdef class Collection:

    def __init__(self, directory: str, parameter: Parameter):
        cdef int fileLimit, j
        cdef list files
        cdef str fileName
        cdef Document document
        self._name = directory
        self._indexType = parameter.getIndexType()
        self._comparator = parameter.getWordComparator()
        self._parameter = parameter
        self._documents = []
        for root, dirs, files in os.walk(directory):
            fileLimit = len(files)
            if parameter.limitNumberOfDocumentsLoaded():
                fileLimit = parameter.getDocumentLimit()
            j = 0
            files.sort()
            for file in files:
                if j >= fileLimit:
                    break
                fileName = os.path.join(root, file)
                if file.endswith(".txt"):
                    document = Document(fileName, file, j)
                    self._documents.append(document)
                    j = j + 1
        if parameter.loadIndexesFromFile():
            self._dictionary = TermDictionary(self._comparator, directory)
            self._invertedIndex = InvertedIndex(directory)
            if parameter.constructPositionalIndex():
                self._positionalIndex = PositionalIndex(directory)
            if parameter.constructPhraseIndex():
                self._phraseDictionary = TermDictionary(self._comparator, directory + "-phrase")
                self._phraseIndex = InvertedIndex(directory + "-phrase")
                if parameter.constructPositionalIndex():
                    self._phrasePositionalIndex = PositionalIndex(directory + "-phrase")
            if parameter.constructNGramIndex():
                self._biGramDictionary = TermDictionary(self._comparator, directory + "-biGram")
                self._triGramDictionary = TermDictionary(self._comparator, directory + "-triGram")
                self._biGramIndex = NGramIndex(directory + "-biGram")
                self._triGramIndex = NGramIndex(directory + "-triGram")
        elif parameter.constructDictionaryInDisk():
            self.constructDictionaryInDisk()
        elif parameter.constructIndexInDisk():
            self.constructIndexesInDisk()
        else:
            self.constructIndexesInMemory()

    cpdef int size(self):
        return len(self._documents)

    cpdef int vocabularySize(self):
        return self._dictionary.size()

    cpdef save(self):
        if self._indexType == IndexType.INVERTED_INDEX:
            self._dictionary.save(self._name)
            self._invertedIndex.save(self._name)
            if self._parameter.constructPositionalIndex():
                self._positionalIndex.save(self._name)
            if self._parameter.constructPhraseIndex():
                self._phraseDictionary.save(self._name + "-phrase")
                self._phraseIndex.save(self._name + "-phrase")
                if self._parameter.constructPositionalIndex():
                    self._phrasePositionalIndex.save(self._name + "-phrase")
            if self._parameter.constructNGramIndex():
                self._biGramDictionary.save(self._name + "-biGram")
                self._triGramDictionary.save(self._name + "-triGram")
                self._biGramIndex.save(self._name + "-biGram")
                self._triGramIndex.save(self._name + "-triGram")

    cpdef constructDictionaryInDisk(self):
        self.constructDictionaryAndInvertedIndexInDisk(TermType.TOKEN)
        if self._parameter.constructPositionalIndex():
            self.constructDictionaryAndPositionalIndexInDisk(TermType.TOKEN)
        if self._parameter.constructPhraseIndex():
            self.constructDictionaryAndInvertedIndexInDisk(TermType.PHRASE)
            if self._parameter.constructPositionalIndex():
                self.constructDictionaryAndPositionalIndexInDisk(TermType.PHRASE)
        if self._parameter.constructNGramIndex():
            self.constructNGramDictionaryAndIndexInDisk()

    cpdef constructIndexesInDisk(self):
        cdef set wordList
        wordList = self.constructDistinctWordList(TermType.TOKEN)
        self._dictionary = TermDictionary(self._comparator, wordList)
        self.constructInvertedIndexInDisk(self._dictionary, TermType.TOKEN)
        if self._parameter.constructPositionalIndex():
            self.constructPositionalIndexInDisk(self._dictionary, TermType.TOKEN)
        if self._parameter.constructPhraseIndex():
            wordList = self.constructDistinctWordList(TermType.PHRASE)
            self._phraseDictionary = TermDictionary(self._comparator, wordList)
            self.constructInvertedIndexInDisk(self._phraseDictionary, TermType.PHRASE)
            if self._parameter.constructPositionalIndex():
                self.constructPositionalIndexInDisk(self._phraseDictionary, TermType.PHRASE)
        if self._parameter.constructNGramIndex():
            self.constructNGramIndex()

    cpdef constructIndexesInMemory(self):
        cdef list terms
        terms = self.constructTerms(TermType.TOKEN)
        self._dictionary = TermDictionary(self._comparator, terms)
        if self._indexType == IndexType.INCIDENCE_MATRIX:
            self._incidenceMatrix = IncidenceMatrix(terms, self._dictionary, len(self._documents))
        elif self._indexType == IndexType.INVERTED_INDEX:
            self._invertedIndex = InvertedIndex(self._dictionary, terms)
            if self._parameter.constructPositionalIndex():
                self._positionalIndex = PositionalIndex(self._dictionary, terms)
            if self._parameter.constructPhraseIndex():
                terms = self.constructTerms(TermType.PHRASE)
                self._phraseDictionary = TermDictionary(self._comparator, terms)
                self._phraseIndex = InvertedIndex(self._phraseDictionary, terms)
                if self._parameter.constructPositionalIndex():
                    self._phrasePositionalIndex = PositionalIndex(self._phraseDictionary, terms)
            if self._parameter.constructNGramIndex():
                self.constructNGramIndex()

    cpdef list constructTerms(self, object termType):
        cdef list terms
        cdef Document doc
        cdef DocumentText documentText
        cdef list docTerms
        terms = []
        for doc in self._documents:
            documentText = doc.loadDocument()
            docTerms = documentText.constructTermList(doc.getDocId(), termType)
            terms.extend(docTerms)
        terms.sort(key=cmp_to_key(TermOccurrence.termOccurrenceComparator))
        return terms

    cpdef set constructDistinctWordList(self, object termType):
        cdef set words, docWords
        cdef Document doc
        cdef DocumentText documentText
        words = set()
        for doc in self._documents:
            documentText = doc.loadDocument()
            docWords = documentText.constructDistinctWordList(termType)
            words = words.union(docWords)
        return words

    cpdef bint notCombinedAllIndexes(self, list currentIdList):
        cdef int _id
        for _id in currentIdList:
            if _id != -1:
                return True
        return False

    cpdef bint notCombinedAllDictionaries(self, list currentWords):
        cdef str word
        for word in currentWords:
            if word is not None:
                return True
        return False

    cpdef list selectIndexesWithMinimumTermIds(self, list currentIdList):
        cdef list result
        cdef int _id
        cdef float _min
        result = []
        _min = float('inf')
        for _id in currentIdList:
            if _id != -1 and _id < _min:
                _min = _id
        for i in range(len(currentIdList)):
            if currentIdList[i] == _min:
                result.append(i)
        return result

    cpdef list selectDictionariesWithMinimumWords(self, list currentWords):
        cdef list result
        cdef str _min, word
        cdef int i
        result = []
        _min = None
        for word in currentWords:
            if word is not None and (_min is None or self._comparator(Word(word), Word(_min)) < 0):
                _min = word
        for i in range(len(currentWords)):
            if currentWords[i] is not None and currentWords[i] == _min:
                result.append(i)
        return result

    cpdef combineMultipleDictionariesInDisk(self,
                                          str name,
                                          str tmpName,
                                          int blockCount):
        cdef list currentIdList
        cdef list currentWords
        cdef list indexesToCombine
        cdef int i
        cdef str line
        currentIdList = []
        currentWords = []
        files = []
        outFile = open(name + "-dictionary.txt", mode="w", encoding="utf-8")
        for i in range(blockCount):
            files.append(open("tmp-" + tmpName + i.__str__() + "-dictionary.txt", mode="r", encoding="utf-8"))
            line = files[i].readline().strip()
            currentIdList.append(int(line[0:line.index(" ")]))
            currentWords.append(line[line.index(" ") + 1:])
        while self.notCombinedAllDictionaries(currentWords):
            indexesToCombine = self.selectDictionariesWithMinimumWords(currentWords)
            outFile.write(currentIdList[indexesToCombine[0]].__str__() + " " + currentWords[indexesToCombine[0]] + "\n")
            for i in indexesToCombine:
                line = files[i].readline().strip()
                if line != "":
                    currentIdList[i] = int(line[0:line.index(" ")])
                    currentWords[i] = line[line.index(" ") + 1:]
                else:
                    currentWords[i] = None
        for i in range(blockCount):
            files[i].close()
        outFile.close()

    cpdef addNGramsToDictionaryAndIndex(self,
                                      str line,
                                      int k,
                                      TermDictionary nGramDictionary,
                                      NGramIndex nGramIndex):
        cdef int wordId, wordIndex, termId
        cdef str word
        cdef list biGrams
        cdef TermOccurrence term
        wordId = int(line[0:line.index(" ")])
        word = line[line.index(" ") + 1:]
        biGrams = TermDictionary.constructNGrams(word, wordId, k)
        for term in biGrams:
            wordIndex = nGramDictionary.getWordIndex(term.getTerm().getName())
            if wordIndex != -1:
                termId = nGramDictionary.getWordWithIndex(wordIndex).getTermId()
            else:
                termId = term.getTerm().getName().__hash__() % (2 ** 24)
                nGramDictionary.addTerm(term.getTerm().getName(), termId)
            nGramIndex.add(termId, wordId)

    cpdef constructNGramDictionaryAndIndexInDisk(self):
        cdef int i, blockCount
        cdef TermDictionary biGramDictionary, triGramDictionary
        cdef NGramIndex biGramIndex, triGramIndex
        cdef str line
        i = 0
        blockCount = 0
        biGramDictionary = TermDictionary(self._comparator)
        triGramDictionary = TermDictionary(self._comparator)
        biGramIndex = NGramIndex()
        triGramIndex = NGramIndex()
        infile = open(self._name + "-dictionary.txt")
        line = infile.readline().strip()
        while line:
            if i < self._parameter.getWordLimit():
                i = i + 1
            else:
                biGramDictionary.save("tmp-biGram-" + blockCount.__str__())
                triGramDictionary.save("tmp-triGram-" + blockCount.__str__())
                biGramDictionary = TermDictionary(self._comparator)
                triGramDictionary = TermDictionary(self._comparator)
                biGramIndex.save("tmp-biGram-" + blockCount.__str__())
                biGramIndex = NGramIndex()
                triGramIndex.save("tmp-triGram-" + blockCount.__str__())
                triGramIndex = NGramIndex()
                blockCount = blockCount + 1
                i = 0
            self.addNGramsToDictionaryAndIndex(line, 2, biGramDictionary, biGramIndex)
            self.addNGramsToDictionaryAndIndex(line, 3, triGramDictionary, triGramIndex)
            line = infile.readline().strip()
        infile.close()
        if len(self._documents) != 0:
            biGramDictionary.save("tmp-biGram-" + blockCount.__str__())
            triGramDictionary.save("tmp-triGram-" + blockCount.__str__())
            biGramIndex.save("tmp-biGram-" + blockCount.__str__())
            triGramIndex.save("tmp-triGram-" + blockCount.__str__())
            blockCount = blockCount + 1
        self.combineMultipleDictionariesInDisk(self._name + "-biGram", "biGram-", blockCount)
        self.combineMultipleDictionariesInDisk(self._name + "-triGram", "triGram-", blockCount)
        self.combineMultipleInvertedIndexesInDisk(self._name + "-biGram", "biGram-", blockCount)
        self.combineMultipleInvertedIndexesInDisk(self._name + "-triGram", "triGram-", blockCount)

    cpdef combineMultipleInvertedIndexesInDisk(self,
                                             str name,
                                             str tmpName,
                                             int blockCount):
        cdef list currentIdList, currentPostingLists, files, items, indexesToCombine
        cdef PostingList mergedPostingList
        cdef int i
        cdef str line
        currentIdList = []
        currentPostingLists = []
        files = []
        outFile = open(name + "-postings.txt", mode="w", encoding="utf-8")
        for i in range(blockCount):
            files.append(open("tmp-" + tmpName + i.__str__() + "-postings.txt", mode="r", encoding="utf-8"))
            line = files[i].readline().strip()
            items = line.split(" ")
            currentIdList.append(int(items[0]))
            line = files[i].readline().strip()
            currentPostingLists.append(PostingList(line))
        while self.notCombinedAllIndexes(currentIdList):
            indexesToCombine = self.selectIndexesWithMinimumTermIds(currentIdList)
            mergedPostingList = currentPostingLists[indexesToCombine[0]]
            for i in range(1, len(indexesToCombine)):
                mergedPostingList = mergedPostingList.union(currentPostingLists[indexesToCombine[i]])
            mergedPostingList.writeToFile(outFile, currentIdList[indexesToCombine[0]])
            for i in indexesToCombine:
                line = files[i].readline().strip()
                if line != "":
                    items = line.split(" ")
                    currentIdList[i] = int(items[0])
                    line = files[i].readline().strip()
                    currentPostingLists[i] = PostingList(line)
                else:
                    currentIdList[i] = -1
        for i in range(blockCount):
            files[i].close()
        outFile.close()

    cpdef constructInvertedIndexInDisk(self,
                                     TermDictionary dictionary,
                                     object termType):
        cdef int i, blockCount, termId
        cdef InvertedIndex invertedIndex
        cdef Document doc
        cdef DocumentText documentText
        cdef set wordList
        cdef str word
        i = 0
        blockCount = 0
        invertedIndex = InvertedIndex()
        for doc in self._documents:
            if i < self._parameter.getDocumentLimit():
                i = i + 1
            else:
                invertedIndex.saveSorted("tmp-" + blockCount.__str__())
                invertedIndex = InvertedIndex()
                blockCount = blockCount + 1
                i = 0
            documentText = doc.loadDocument()
            wordList = documentText.constructDistinctWordList(termType)
            for word in wordList:
                termId = dictionary.getWordIndex(word)
                invertedIndex.add(termId, doc.getDocId())
        if len(self._documents) != 0:
            invertedIndex.saveSorted("tmp-" + blockCount.__str__())
            blockCount = blockCount + 1
        if termType == TermType.TOKEN:
            self.combineMultipleInvertedIndexesInDisk(self._name, "", blockCount)
        else:
            self.combineMultipleInvertedIndexesInDisk(self._name + "-phrase", "", blockCount)

    cpdef constructDictionaryAndInvertedIndexInDisk(self, object termType):
        cdef int i, blockCount, termId
        cdef InvertedIndex invertedIndex
        cdef TermDictionary dictionary
        cdef Document doc
        cdef DocumentText documentText
        cdef set wordList
        cdef str word
        i = 0
        blockCount = 0
        invertedIndex = InvertedIndex()
        dictionary = TermDictionary(self._comparator)
        for doc in self._documents:
            if i < self._parameter.getDocumentLimit():
                i = i + 1
            else:
                dictionary.save("tmp-" + blockCount.__str__())
                dictionary = TermDictionary(self._comparator)
                invertedIndex.saveSorted("tmp-" + blockCount.__str__())
                invertedIndex = InvertedIndex()
                blockCount = blockCount + 1
                i = 0
            documentText = doc.loadDocument()
            wordList = documentText.constructDistinctWordList(termType)
            for word in wordList:
                wordIndex = dictionary.getWordIndex(word)
                if wordIndex != -1:
                    termId = dictionary.getWordWithIndex(wordIndex).getTermId()
                else:
                    termId = word.__hash__() % (2 ** 24)
                    dictionary.addTerm(word, termId)
                invertedIndex.add(termId, doc.getDocId())
        if len(self._documents) != 0:
            dictionary.save("tmp-" + blockCount.__str__())
            invertedIndex.saveSorted("tmp-" + blockCount.__str__())
            blockCount = blockCount + 1
        if termType == TermType.TOKEN:
            self.combineMultipleDictionariesInDisk(self._name, "", blockCount)
            self.combineMultipleInvertedIndexesInDisk(self._name, "", blockCount)
        else:
            self.combineMultipleDictionariesInDisk(self._name + "-phrase", "", blockCount)
            self.combineMultipleInvertedIndexesInDisk(self._name + "-phrase", "", blockCount)

    cpdef combineMultiplePositionalIndexesInDisk(self, str name, int blockCount):
        cdef list currentIdList, currentPostingLists, files, items, indexesToCombine
        cdef int i
        cdef str line
        cdef PositionalPostingList mergedPostingList
        currentIdList = []
        currentPostingLists = []
        files = []
        outFile = open(name + "-positionalPostings.txt", mode="w", encoding="utf-8")
        for i in range(blockCount):
            files.append(open("tmp-" + i.__str__() + "-positionalPostings.txt", mode="r", encoding="utf-8"))
            line = files[i].readline().strip()
            items = line.split(" ")
            currentIdList.append(int(items[0]))
            currentPostingLists.append(PositionalPostingList(files[i], int(items[1])))
        while self.notCombinedAllIndexes(currentIdList):
            indexesToCombine = self.selectIndexesWithMinimumTermIds(currentIdList)
            mergedPostingList = currentPostingLists[indexesToCombine[0]]
            for i in range(1, len(indexesToCombine)):
                mergedPostingList = mergedPostingList.union(currentPostingLists[indexesToCombine[i]])
            mergedPostingList.writeToFile(outFile, currentIdList[indexesToCombine[0]])
            for i in indexesToCombine:
                line = files[i].readline().strip()
                if line != "":
                    items = line.split(" ")
                    currentIdList[i] = int(items[0])
                    currentPostingLists[i] = PositionalPostingList(files[i], int(items[1]))
                else:
                    currentIdList[i] = -1
        for i in range(blockCount):
            files[i].close()
        outFile.close()

    cpdef constructDictionaryAndPositionalIndexInDisk(self, object termType):
        cdef int i, blockCount, wordIndex, termId
        cdef PositionalIndex positionalIndex
        cdef TermDictionary termDictionary
        cdef Document doc
        cdef DocumentText documentText
        cdef list terms
        cdef TermOccurrence termOccurrence
        i = 0
        blockCount = 0
        positionalIndex = PositionalIndex()
        dictionary = TermDictionary(self._comparator)
        for doc in self._documents:
            if i < self._parameter.getDocumentLimit():
                i = i + 1
            else:
                dictionary.save("tmp-" + blockCount.__str__())
                dictionary = TermDictionary(self._comparator)
                positionalIndex.saveSorted("tmp-" + blockCount.__str__())
                positionalIndex = PositionalIndex()
                blockCount = blockCount + 1
                i = 0
            documentText = doc.loadDocument()
            terms = documentText.constructTermList(doc.getDocId(), termType)
            for termOccurrence in terms:
                wordIndex = dictionary.getWordIndex(termOccurrence.getTerm().getName())
                if wordIndex != -1:
                    termId = dictionary.getWordWithIndex(wordIndex).getTermId()
                else:
                    termId = termOccurrence.getTerm().getName().__hash__() % (2 ** 24)
                    dictionary.addTerm(termOccurrence.getTerm().getName(), termId)
                positionalIndex.addPosition(termId, termOccurrence.getDocId(), termOccurrence.getPosition())
        if len(self._documents) != 0:
            dictionary.save("tmp-" + blockCount.__str__())
            positionalIndex.saveSorted("tmp-" + blockCount.__str__())
            blockCount = blockCount + 1
        if termType == TermType.TOKEN:
            self.combineMultipleDictionariesInDisk(self._name, "", blockCount)
            self.combineMultiplePositionalIndexesInDisk(self._name, blockCount)
        else:
            self.combineMultipleDictionariesInDisk(self._name + "-phrase", "", blockCount)
            self.combineMultiplePositionalIndexesInDisk(self._name + "-phrase", blockCount)

    cpdef constructPositionalIndexInDisk(self, TermDictionary dictionary, object termType):
        cdef int i, blockCount, termId
        cdef PositionalIndex positionalIndex
        cdef Document doc
        cdef DocumentText documentText
        cdef list terms
        cdef TermOccurrence termOccurrence
        i = 0
        blockCount = 0
        positionalIndex = PositionalIndex()
        for doc in self._documents:
            if i < self._parameter.getDocumentLimit():
                i = i + 1
            else:
                positionalIndex.saveSorted("tmp-" + blockCount.__str__())
                positionalIndex = PositionalIndex()
                blockCount = blockCount + 1
                i = 0
            documentText = doc.loadDocument()
            terms = documentText.constructTermList(doc.getDocId(), termType)
            for termOccurrence in terms:
                termId = dictionary.getWordIndex(termOccurrence.getTerm().getName())
                positionalIndex.addPosition(termId, termOccurrence.getDocId(), termOccurrence.getPosition())
        if len(self._documents) != 0:
            positionalIndex.saveSorted("tmp-" + blockCount.__str__())
            blockCount = blockCount + 1
        if termType == TermType.TOKEN:
            self.combineMultiplePositionalIndexesInDisk(self._name, blockCount)
        else:
            self.combineMultiplePositionalIndexesInDisk(self._name + "-phrase", blockCount)

    cpdef constructNGramIndex(self):
        cdef list terms
        terms = self._dictionary.constructTermsFromDictionary(2)
        self._biGramDictionary = TermDictionary(self._comparator, terms)
        self._biGramIndex = NGramIndex(self._biGramDictionary, terms)
        terms = self._dictionary.constructTermsFromDictionary(3)
        self._triGramDictionary = TermDictionary(self._comparator, terms)
        self._triGramIndex = NGramIndex(self._triGramDictionary, terms)

    cpdef searchCollection(self,
                         Query query,
                         object retrievalType,
                         object termWeighting,
                         object documentWeighting):
        if self._indexType == IndexType.INCIDENCE_MATRIX:
            return self._incidenceMatrix.search(query, self._dictionary)
        else:
            if retrievalType == RetrievalType.BOOLEAN:
                return self._invertedIndex.search(query, self._dictionary)
            elif retrievalType == RetrievalType.POSITIONAL:
                return self._positionalIndex.positionalSearch(query, self._dictionary)
            else:
                return self._positionalIndex.rankedSearch(query,
                                                          self._dictionary,
                                                          self._documents,
                                                          termWeighting,
                                                          documentWeighting)
