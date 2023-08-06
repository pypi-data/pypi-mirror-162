import multiprocessing
import queue
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from uuid import uuid4

T = TypeVar("T")


class Queue(Generic[T]):
    def __init__(
        self,
        queue: Union["queue.Queue[T]", "multiprocessing.Queue[T]"],
        name: str = str(uuid4()),
    ) -> None:
        self.queue = queue
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def get(self, *args, **kwargs) -> T:
        return self.queue.get(*args, **kwargs)

    def put(self, item: T, *args, **kwargs) -> None:
        self.queue.put(item, *args, **kwargs)

    def __len__(self) -> int:
        return self.queue.qsize()


class QueuePutStrategy(ABC, Generic[T]):
    @abstractmethod
    def put(self, queue: Queue[T], item: T):
        pass


class PutBlocking(QueuePutStrategy[T]):
    def __init__(self, timeout: int = None) -> None:
        self.timeout = timeout

    def put(self, queue: Queue[T], item: T):
        queue.put(item, block=True, timeout=self.timeout)


class PutNonBlocking(QueuePutStrategy[T]):
    def put(self, queue: Queue[T], item: T):
        queue.put(item, block=False)


class QueueGetStrategy(ABC, Generic[T]):
    @abstractmethod
    def get(self, queue: Queue[T]) -> T:
        pass


class GetBlocking(QueueGetStrategy[T]):
    def __init__(self, timeout: int = None) -> None:
        self.timeout = timeout

    def get(self, queue: Queue[T]) -> T:
        return queue.get(block=True, timeout=self.timeout)


class GetNonBlocking(QueueGetStrategy[T]):
    def get(self, queue: Queue[T]) -> T:
        return queue.get(block=False)
