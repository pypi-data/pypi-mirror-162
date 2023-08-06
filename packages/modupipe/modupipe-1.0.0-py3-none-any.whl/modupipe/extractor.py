from __future__ import annotations

from abc import ABC, abstractmethod
from random import random
from typing import Generic, Iterator, List, Tuple, TypeVar

from modupipe.exceptions import MaxIterationsReached
from modupipe.mapper import Mapper
from modupipe.queue import Queue, QueueGetStrategy

Data = TypeVar("Data")
MappedData = TypeVar("MappedData")


class Extractor(ABC, Generic[Data]):
    @abstractmethod
    def extract(self) -> Iterator[Data]:
        pass

    def __add__(self, mapper: Mapper[Data, MappedData]) -> Extractor[MappedData]:
        return MappedExtractor(self, mapper)


class MappedExtractor(Extractor[MappedData], Generic[Data, MappedData]):
    def __init__(
        self, extractor: Extractor[Data], mapper: Mapper[Data, MappedData]
    ) -> None:
        self.extractor = extractor
        self.mapper = mapper

    def extract(self) -> Iterator[MappedData]:
        return self.mapper.map(self.extractor.extract())


class ExtractorList(Extractor[Tuple[Data, ...]], Generic[Data]):
    def __init__(self, extractors: List[Extractor[Data]]) -> None:
        self.extractors = extractors

    def extract(self) -> Iterator[Tuple[Data, ...]]:
        iterators = (source.extract() for source in self.extractors)
        for items in zip(*iterators):
            yield items


class GetFromQueue(Extractor[Data]):
    def __init__(self, queue: Queue[Data], strategy: QueueGetStrategy[Data]) -> None:
        self.queue = queue
        self.strategy = strategy

    def extract(self) -> Iterator[Data]:
        while True:
            yield self.strategy.get(self.queue)


class Random(Extractor[float]):
    def extract(self) -> Iterator[float]:
        while True:
            yield random()


class MaxIterations(Extractor[Data]):
    def __init__(self, extractor: Extractor[Data], nb_iterations: int) -> None:
        self.extractor = extractor
        self.nb_iterations = nb_iterations

    def extract(self) -> Iterator[Data]:
        for i, item in enumerate(self.extractor.extract()):
            if i >= self.nb_iterations:
                raise MaxIterationsReached()

            yield item
