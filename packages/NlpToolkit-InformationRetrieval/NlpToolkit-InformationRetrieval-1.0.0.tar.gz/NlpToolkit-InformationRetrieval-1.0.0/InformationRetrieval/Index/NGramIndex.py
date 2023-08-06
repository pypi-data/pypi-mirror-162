from InformationRetrieval.Index.InvertedIndex import InvertedIndex
from InformationRetrieval.Index.TermOccurrence import TermOccurrence


class NGramIndex(InvertedIndex):

    def __init__(self,
                 dictionaryOrfileName: object = None,
                 terms: [TermOccurrence] = None):
        super().__init__(dictionaryOrfileName, terms)
