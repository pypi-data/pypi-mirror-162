from Dictionary.Word import Word
from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer
from MorphologicalDisambiguation.MorphologicalDisambiguator import MorphologicalDisambiguator

from InformationRetrieval.Document.IndexType import IndexType
from InformationRetrieval.Index.TermOccurrence import TermOccurrence


class Parameter:

    _indexType: IndexType = IndexType.INVERTED_INDEX
    _wordComparator: object
    _loadIndexesFromFile: bool = False
    _disambiguator: MorphologicalDisambiguator
    _fsm: FsmMorphologicalAnalyzer
    _normalizeDocument: bool = False
    _phraseIndex: bool = True
    _positionalIndex: bool = True
    _constructNGramIndex: bool = True
    _constructIndexInDisk: bool = False
    _constructDictionaryInDisk: bool = False
    _limitNumberOfDocumentsLoaded: bool = False
    _documentLimit: int = 1000
    _wordLimit: int = 10000

    def __init__(self):
        self._wordComparator = TermOccurrence.ignoreCaseComparator
        pass

    def getIndexType(self) -> IndexType:
        return self._indexType

    def getWordComparator(self) -> object:
        return self._wordComparator

    def loadIndexesFromFile(self) -> bool:
        return self._loadIndexesFromFile

    def getDisambiguator(self) -> MorphologicalDisambiguator:
        return self._disambiguator

    def getFsm(self) -> FsmMorphologicalAnalyzer:
        return self._fsm

    def constructPhraseIndex(self) -> bool:
        return self._phraseIndex

    def normalizeDocument(self) -> bool:
        return self._normalizeDocument

    def constructPositionalIndex(self) -> bool:
        return self._positionalIndex

    def constructNGramIndex(self) -> bool:
        return self._constructNGramIndex

    def constructIndexInDisk(self) -> bool:
        return self._constructIndexInDisk

    def limitNumberOfDocumentsLoaded(self) -> bool:
        return self._limitNumberOfDocumentsLoaded

    def getDocumentLimit(self) -> int:
        return self._documentLimit

    def constructDictionaryInDisk(self) -> bool:
        return self._constructDictionaryInDisk

    def getWordLimit(self) -> int:
        return self._wordLimit

    def setIndexType(self, indexType: IndexType):
        self._indexType = indexType

    def setWordComparator(self, wordComparator: object):
        self._wordComparator = wordComparator

    def setLoadIndexesFromFile(self, loadIndexesFromFile: bool):
        self._loadIndexesFromFile = loadIndexesFromFile

    def setDisambiguator(self, disambiguator: MorphologicalDisambiguator):
        self._disambiguator = disambiguator

    def setFsm(self, fsm: FsmMorphologicalAnalyzer):
        self._fsm = fsm

    def setNormalizeDocument(self, normalizeDocument: bool):
        self._normalizeDocument = normalizeDocument

    def setPhraseIndex(self, phraseIndex: bool):
        self._phraseIndex = phraseIndex

    def setPositionalIndex(self, positionalIndex: bool):
        self._positionalIndex = positionalIndex

    def setNGramIndex(self, nGramIndex: bool):
        self._constructNGramIndex = nGramIndex

    def setConstructIndexInDisk(self, constructIndexInDisk: bool):
        self._constructIndexInDisk = constructIndexInDisk

    def setLimitNumberOfDocumentsLoaded(self, limitNumberOfDocumentsLoaded: bool):
        self._limitNumberOfDocumentsLoaded = limitNumberOfDocumentsLoaded

    def setDocumentLimit(self, documentLimit: int):
        self._documentLimit = documentLimit

    def setConstructDictionaryInDisk(self, constructDictionaryInDisk: bool):
        self._constructDictionaryInDisk = constructDictionaryInDisk
        if self._constructDictionaryInDisk:
            self._constructIndexInDisk = True

    def setWordLimit(self, wordLimit: int):
        self._wordLimit = wordLimit
