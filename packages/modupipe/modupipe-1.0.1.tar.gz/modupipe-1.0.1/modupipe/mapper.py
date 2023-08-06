from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Iterator, List, TypeVar

from modupipe.base import Condition
from modupipe.loader import Loader
from modupipe.queue import Queue, QueuePutStrategy

Input = TypeVar("Input")
Output = TypeVar("Output")
NextOutput = TypeVar("NextOutput")


class Mapper(ABC, Generic[Input, Output]):
    @abstractmethod
    def map(self, items: Iterator[Input]) -> Iterator[Output]:
        pass

    def __add__(self, next: Mapper[Output, NextOutput]) -> Mapper[Input, NextOutput]:
        return ChainedMapper(self, next)


IdentityMapper = Mapper[Input, Input]


class ChainedMapper(Mapper[Input, NextOutput], Generic[Input, Output, NextOutput]):
    def __init__(
        self, mapper: Mapper[Input, Output], next: Mapper[Output, NextOutput]
    ) -> None:
        self.mapper = mapper
        self.next = next

    def map(self, input: Iterator[Input]) -> Iterator[NextOutput]:
        output = self.mapper.map(input)
        return self.next.map(output)


class Filter(IdentityMapper[Input]):
    def __init__(self, condition: Condition[Input]) -> None:
        self.condition = condition

    def map(self, items: Iterator[Input]) -> Iterator[Input]:
        for item in items:
            if self.condition.check(item):
                yield item


class ToString(Mapper[Input, str]):
    def map(self, items: Iterator[Input]) -> Iterator[str]:
        for item in items:
            yield str(item)


class Print(IdentityMapper[Input]):
    def map(self, items: Iterator[Input]) -> Iterator[Input]:
        for item in items:
            print(item)
            yield item


class Buffer(Mapper[Input, List[Input]]):
    def __init__(self, size: int) -> None:
        self.size = size
        self.buffer: List[Input] = []

    def map(self, items: Iterator[Input]) -> Iterator[List[Input]]:
        for item in items:
            self.buffer.append(item)

            if len(self.buffer) >= self.size:
                yield self.buffer
                self.buffer = []


class PutToQueue(IdentityMapper[Input]):
    def __init__(self, queue: Queue[Input], strategy: QueuePutStrategy) -> None:
        self.queue = queue
        self.strategy = strategy

    def map(self, items: Iterator[Input]) -> Iterator[Input]:
        for item in items:
            self.strategy.put(self.queue, item)
            yield item


class PushTo(IdentityMapper[Input]):
    def __init__(self, loader: Loader[Input, Any]) -> None:
        self.loader = loader

    def map(self, items: Iterator[Input]) -> Iterator[Input]:
        for item in items:
            self.loader.load(item)
            yield item


class PushToAndMap(Mapper[Input, Output]):
    def __init__(self, loader: Loader[Input, Output]) -> None:
        self.loader = loader

    def map(self, items: Iterator[Input]) -> Iterator[Output]:
        for item in items:
            yield self.loader.load(item)
