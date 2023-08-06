from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

from modupipe.base import Condition
from modupipe.queue import Queue, QueuePutStrategy

Input = TypeVar("Input")
Output = TypeVar("Output")
NextOutput = TypeVar("NextOutput")


class Loader(ABC, Generic[Input, Output]):
    @abstractmethod
    def load(self, item: Input) -> Output:
        pass

    def __add__(self, next: Loader[Output, NextOutput]) -> Loader[Input, NextOutput]:
        return ChainedLoader(self, next)


IdentityLoader = Loader[Input, Input]
Sink = Loader[Input, Any]


class ChainedLoader(Loader[Input, NextOutput], Generic[Input, Output, NextOutput]):
    def __init__(
        self, mapper: Loader[Input, Output], next: Loader[Output, NextOutput]
    ) -> None:
        self.mapper = mapper
        self.next = next

    def load(self, item: Input) -> NextOutput:
        mapped_item = self.mapper.load(item)
        return self.next.load(mapped_item)


class OnCondition(Loader[Input, Optional[Output]]):
    def __init__(
        self, condition: Condition[Input], loader: Loader[Input, Output]
    ) -> None:
        self.condition = condition
        self.loader = loader

    def load(self, item: Input) -> Optional[Output]:
        if self.condition.check(item):
            return self.loader.load(item)
        else:
            return None


class LoaderList(Loader[Input, List[Output]]):
    def __init__(self, loaders: List[Loader[Input, Output]]) -> None:
        self.loaders = loaders

    def load(self, item: Input) -> List[Output]:
        return [loader.load(item) for loader in self.loaders]


class LoaderListUntyped(Loader[Input, List[Any]]):
    def __init__(self, loaders: List[Loader[Input, Any]]) -> None:
        self.loaders = loaders

    def load(self, item: Input) -> List[Any]:
        return [loader.load(item) for loader in self.loaders]


class ToString(Loader[Input, str]):
    def load(self, item: Input) -> str:
        return str(item)


class Print(IdentityLoader[Input]):
    def load(self, item: Input) -> Input:
        print(item)
        return item


class Buffer(Loader[Input, Optional[List[Input]]]):
    def __init__(self, size: int) -> None:
        self.size = size
        self.buffer: List[Input] = []

    def load(self, item: Input) -> Optional[List[Input]]:
        self.buffer.append(item)

        if len(self.buffer) >= self.size:
            items = self.buffer
            self.buffer = []
            return items
        else:
            return None


class PutToQueue(IdentityLoader[Input]):
    def __init__(self, queue: Queue[Input], strategy: QueuePutStrategy) -> None:
        self.queue = queue
        self.strategy = strategy

    def load(self, item: Input) -> Input:
        self.strategy.put(self.queue, item)
        return item
