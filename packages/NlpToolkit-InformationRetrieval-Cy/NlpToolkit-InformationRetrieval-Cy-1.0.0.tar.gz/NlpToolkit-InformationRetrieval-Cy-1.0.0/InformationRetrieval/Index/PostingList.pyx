from InformationRetrieval.Index.Posting cimport Posting

cdef class PostingList:

    @staticmethod
    def postingListComparator(listA: PostingList, listB: PostingList):
        if listA.size() < listB.size():
            return -1
        else:
            if listA.size() < listB.size():
                return 1
            else:
                return 0

    def __init__(self, line: str = None):
        cdef str _id
        self._postings = []
        if line is not None:
            ids = line.split(" ")
            for _id in ids:
                self.add(int(_id))

    cpdef add(self, int docId):
        self._postings.append(Posting(docId))

    cpdef int size(self):
        return len(self._postings)

    cpdef PostingList intersection(self, PostingList secondList):
        cdef int i, j
        cdef PostingList result
        cdef Posting p1, p2
        i = 0
        j = 0
        result = PostingList()
        while i < self.size() and j < secondList.size():
            p1 = self._postings[i]
            p2 = secondList._postings[j]
            if p1.getId() == p2.getId():
                result.add(p1.getId())
                i = i + 1
                j = j + 1
            else:
                if p1.getId() < p2.getId():
                    i = i + 1
                else:
                    j = j + 1
        return result

    cpdef PostingList union(self, PostingList secondList):
        cdef PostingList result
        result = PostingList()
        result._postings.extend(self._postings)
        result._postings.extend(secondList._postings)
        return result

    cpdef QueryResult toQueryResult(self):
        cdef QueryResult result
        cdef Posting posting
        result = QueryResult()
        for posting in self._postings:
            result.add(posting.getId())
        return result

    cpdef writeToFile(self, object outfile, int index):
        if self.size() > 0:
            outfile.write(index.__str__() + " " + self.size().__str__() + "\n")
            outfile.write(self.__str__())

    def __str__(self):
        cdef str result
        cdef Posting posting
        result = ""
        for posting in self._postings:
            result = result + posting.getId().__str__() + " "
        return result.strip() + "\n"
