from __future__ import annotations
from math import sqrt, log

from InformationRetrieval.Document.DocumentWeighting import DocumentWeighting
from InformationRetrieval.Index.TermWeighting import TermWeighting


class VectorSpaceModel:

    _model: [float]

    def __init__(self,
                 termFrequencies: [int],
                 documentFrequencies: [int],
                 documentSize: int,
                 termWeighting: TermWeighting,
                 documentWeighting: DocumentWeighting):
        _sum = 0
        self._model = []
        for i in range(len(termFrequencies)):
            self._model.append(self.weighting(termFrequencies[i],
                                              documentFrequencies[i],
                                              documentSize,
                                              termWeighting,
                                              documentWeighting))
            _sum = _sum + self._model[i] * self._model[i]
        for i in range(len(termFrequencies)):
            self._model[i] = self._model[i] / sqrt(_sum)

    def get(self, index: int) -> float:
        return self._model[index]

    def cosineSimilarity(self, secondModel: VectorSpaceModel):
        _sum = 0.0
        for i in range(len(self._model)):
            _sum = _sum + self._model[i] * secondModel._model[i]
        return _sum

    @staticmethod
    def weighting(termFrequency: float,
                  documentFrequency: float,
                  documentSize: int,
                  termWeighting: TermWeighting,
                  documentWeighting: DocumentWeighting):
        multiplier1 = 1
        multiplier2 = 1
        if termWeighting == TermWeighting.NATURAL:
            multiplier1 = termFrequency
        elif termWeighting == TermWeighting.LOGARITHM:
            if termFrequency > 0:
                multiplier1 = 1 + log(termFrequency)
            else:
                multiplier1 = 0
        elif termWeighting == TermWeighting.BOOLE:
            if termFrequency > 0:
                multiplier1 = 1
            else:
                multiplier1 = 0
        if documentWeighting == DocumentWeighting.NO_IDF:
            multiplier2 = 1
        elif documentWeighting == DocumentWeighting.IDF:
            multiplier2 = log(documentSize / documentFrequency)
        elif documentWeighting == DocumentWeighting.PROBABILISTIC_IDF:
            if documentSize > 2 * documentFrequency:
                multiplier2 = log((documentSize - documentFrequency) / documentFrequency)
            else:
                multiplier2 = 0
        return multiplier1 * multiplier2
