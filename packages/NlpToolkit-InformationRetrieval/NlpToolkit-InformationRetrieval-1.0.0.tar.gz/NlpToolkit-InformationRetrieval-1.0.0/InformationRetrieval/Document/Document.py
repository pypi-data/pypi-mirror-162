from Corpus.Corpus import Corpus
from Corpus.Sentence import Sentence
from Corpus.TurkishSplitter import TurkishSplitter
from Dictionary.Word import Word
from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer
from MorphologicalDisambiguation.MorphologicalDisambiguator import MorphologicalDisambiguator

from InformationRetrieval.Document.DocumentText import DocumentText


class Document:

    _absoluteFileName: str
    _fileName: str
    _docId: int
    _size: int = 0

    def __init__(self, absoluteFileName: str, fileName: str, docId: int):
        self._absoluteFileName = absoluteFileName
        self._fileName = fileName
        self._docId = docId

    def loadDocument(self) -> DocumentText:
        documentText = DocumentText(self._absoluteFileName, TurkishSplitter())
        self._size = documentText.numberOfWords()
        return documentText

    def normalizeDocument(self,
                          disambiguator: MorphologicalDisambiguator,
                          fsm: FsmMorphologicalAnalyzer) -> Corpus:
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

    def getDocId(self) -> int:
        return self._docId

    def getFileName(self) -> str:
        return self._fileName

    def getAbsoluteFileName(self) -> str:
        return self._absoluteFileName

    def getSize(self) -> int:
        return self._size
