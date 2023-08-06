from Corpus.Corpus import Corpus
from Corpus.SentenceSplitter import SentenceSplitter

from Dictionary.Word import Word

from InformationRetrieval.Index.TermOccurrence import TermOccurrence
from InformationRetrieval.Index.TermType import TermType


class DocumentText(Corpus):

    def __init__(self, fileName: str, sentenceSplitter: SentenceSplitter = None):
        super().__init__(fileName, sentenceSplitter)

    def constructDistinctWordList(self, termType: TermType) -> set:
        words = set()
        for i in range(self.sentenceCount()):
            sentence = self.getSentence(i)
            for j in range(sentence.wordCount()):
                if termType == TermType.TOKEN:
                    words.add(sentence.getWord(j).getName())
                elif termType == TermType.PHRASE:
                    if j < sentence.wordCount() - 1:
                        words.add(sentence.getWord(j).getName() + " " + sentence.getWord(j + 1).getName())
        return words

    def constructTermList(self, docId: int, termType: TermType) -> [TermOccurrence]:
        terms = []
        size = 0
        for i in range(self.sentenceCount()):
            sentence = self.getSentence(i)
            for j in range(sentence.wordCount()):
                if termType == TermType.TOKEN:
                    terms.append(TermOccurrence(sentence.getWord(j), docId, size))
                    size = size + 1
                elif termType == TermType.PHRASE:
                    if j < sentence.wordCount() - 1:
                        terms.append(TermOccurrence(Word(sentence.getWord(j).getName() + " " + sentence.getWord(j + 1).getName()), docId, size))
                        size = size + 1
        return terms
