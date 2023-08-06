from typing import TextIO

from InformationRetrieval.Index.Posting cimport Posting

cdef class PositionalPostingList:

    def __init__(self, infile: TextIO = None, count: int = None):
        cdef int i, j, docId, numberOfPositionalPostings, positionalPosting
        cdef list ids
        cdef str, line
        self._postings = []
        if infile is not None:
            for i in range(count):
                line = infile.readline().strip()
                ids = line.split(" ")
                numberOfPositionalPostings = int(ids[1])
                if len(ids) == numberOfPositionalPostings + 2:
                    docId = int(ids[0])
                    for j in range(numberOfPositionalPostings):
                        positionalPosting = int(ids[j + 2])
                        self.add(docId, positionalPosting)

    cpdef int size(self):
        return len(self._postings)

    cpdef int getIndex(self, int docId):
        cdef int begin, end, middle
        begin = 0
        end = self.size() - 1
        while begin <= end:
            middle = (begin + end) // 2
            if docId == self._postings[middle].getDocId():
                return middle
            else:
                if docId == self._postings[middle].getDocId():
                    end = middle - 1
                else:
                    begin = middle + 1
        return -1

    cpdef QueryResult toQueryResult(self):
        cdef QueryResult result
        cdef PositionalPosting posting
        result = QueryResult()
        for posting in self._postings:
            result.add(posting.getDocId())
        return result

    cpdef add(self, int docId, int position):
        cdef int index
        index = self.getIndex(docId)
        if index == -1:
            self._postings.append(PositionalPosting(docId))
            self._postings[len(self._postings) - 1].add(position)
        else:
            self._postings[index].add(position)

    cpdef PositionalPosting get(self, int index):
        return self._postings[index]

    cpdef PositionalPostingList union(self, PositionalPostingList secondList):
        cdef PositionalPostingList result
        result = PositionalPostingList()
        result._postings.extend(self._postings)
        result._postings.extend(secondList._postings)
        return result

    cpdef PositionalPostingList intersection(self, PositionalPostingList secondList):
        cdef int i, j, position1, position2
        cdef PositionalPostingList result
        cdef PositionalPosting p1, p2
        cdef list postings1, postings2
        cdef Posting posting1, posting2
        i = 0
        j = 0
        result = PositionalPostingList()
        while i < len(self._postings) and j < len(secondList._postings):
            p1 = self._postings[i]
            p2 = secondList._postings[j]
            if p1.getDocId() == p2.getDocId():
                position1 = 0
                position2 = 0
                postings1 = p1.getPositions()
                postings2 = p2.getPositions()
                while position1 < len(postings1) and position2 < len(postings2):
                    posting1: Posting = postings1[position1]
                    posting2: Posting = postings2[position2]
                    if posting1.getId() + 1 == posting2.getId():
                        result.add(p1.getDocId(), posting2.getId())
                        position1 = position1 + 1
                        position2 = position2 + 1
                    else:
                        if posting1.getId() + 1 < posting2.getId():
                            position1 = position1 + 1
                        else:
                            position2 = position2 + 1
                i = i + 1
                j = j + 1
            else:
                if p1.getDocId() < p2.getDocId():
                    i = i + 1
                else:
                    j = j + 1
        return result

    def __str__(self) -> str:
        cdef str result
        cdef PositionalPosting positionalPosting
        result = ""
        for positionalPosting in self._postings:
            result = result + "\t" + positionalPosting.__str__() + "\n"
        return result

    cpdef writeToFile(self, object outfile, int index):
        if self.size() > 0:
            outfile.write(index.__str__() + " " + self.size().__str__() + "\n")
            outfile.write(self.__str__())
