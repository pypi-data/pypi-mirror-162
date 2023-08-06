from functools import cmp_to_key

from Dictionary.Dictionary import Dictionary
from Dictionary.Word import Word

from InformationRetrieval.Index.Term import Term
from InformationRetrieval.Index.TermOccurrence import TermOccurrence


class TermDictionary(Dictionary):

    def __init__(self, comparator: object, fileNameOrTerms = None):
        super().__init__(comparator)
        if fileNameOrTerms is not None:
            if isinstance(fileNameOrTerms, str):
                fileName: str = fileNameOrTerms
                infile = open(fileName + "-dictionary.txt", mode='r', encoding='utf-8')
                line = infile.readline().strip()
                while line != "":
                    termId = int(line[0:line.index(" ")])
                    self.words.append(Term(line[line.index(" ") + 1:], termId))
                    line = infile.readline().strip()
                infile.close()
            else:
                if isinstance(fileNameOrTerms, list):
                    termId = 0
                    terms: [TermOccurrence] = fileNameOrTerms
                    if len(terms) > 0:
                        term = terms[0]
                        self.addTerm(term.getTerm().getName(), termId)
                        termId = termId + 1
                        previousTerm = term
                        i = 1
                        while i < len(terms):
                            term: TermOccurrence = terms[i]
                            if term.isDifferent(previousTerm):
                                self.addTerm(term.getTerm().getName(), termId)
                                termId = termId + 1
                            i = i + 1
                            previousTerm = term
                else:
                    wordList: [Word] = []
                    for word in fileNameOrTerms:
                        wordList.append(Word(word))
                    wordList.sort(key=cmp_to_key(comparator))
                    termID = 0
                    for termWord in wordList:
                        self.addTerm(termWord.getName(), termID)
                        termID = termID + 1

    def __getPosition(self, word: Word) -> int:
        lo = 0
        hi = len(self.words) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.comparator(self.words[mid], word) < 0:
                lo = mid + 1
            elif self.comparator(self.words[mid], word) > 0:
                hi = mid - 1
            else:
                return mid
        return -(lo + 1)

    def addTerm(self, name: str, termId: int):
        middle = self.__getPosition(Word(name))
        if middle < 0:
            self.words.insert(-middle - 1, Term(name, termId))

    def save(self, fileName: str):
        outfile = open(fileName + "-dictionary.txt", mode='w', encoding='utf-8')
        for word in self.words:
            term: Term = word
            outfile.write(term.getTermId().__str__() + " " + term.getName() + "\n")
        outfile.close()

    @staticmethod
    def constructNGrams(word: str, termId: int, k: int) -> [TermOccurrence]:
        nGrams = []
        if len(word) >= k - 1:
            for j in range(-1, len(word) - k + 2):
                if j == -1:
                    term = "$" + word[0:k - 1]
                elif j == len(word) - k + 1:
                    term = word[j: j + k - 1] + "$"
                else:
                    term = word[j: j + k]
                nGrams.append(TermOccurrence(Word(term), termId, j))
        return nGrams

    def constructTermsFromDictionary(self, k: int) -> [TermOccurrence]:
        terms : [TermOccurrence] = []
        for i in range(self.size()):
            word = self.getWordWithIndex(i).getName()
            terms.extend(TermDictionary.constructNGrams(word, i, k))
        terms.sort(key=cmp_to_key(TermOccurrence.termOccurrenceComparator))
        return terms
