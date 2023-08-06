import traceback
from abc import ABC, abstractmethod
from multiprocessing import Process
from threading import Thread
from typing import Generic, List, TypeVar

from modupipe.extractor import Extractor

Data = TypeVar("Data")


class Runnable(ABC):
    @abstractmethod
    def run(self):
        pass


class StepPipeline(Runnable, Generic[Data]):
    def __init__(self, extractor: Extractor[Data]) -> None:
        self.iterator = extractor.extract()

    def run(self):
        try:
            next(self.iterator)
        except StopIteration:
            pass


class FullPipeline(Runnable, Generic[Data]):
    def __init__(self, extractor: Extractor[Data]) -> None:
        self.extractor = extractor

    def run(self):
        for _ in self.extractor.extract():
            pass


class Repeat(Runnable, Generic[Data]):
    def __init__(self, runnable: Runnable, nb_times: int) -> None:
        self.runnable = runnable
        self.nb_repeats = nb_times

    def run(self):
        for _ in range(self.nb_repeats):
            self.runnable.run()


class NamedRunnable(Runnable, Generic[Data]):
    def __init__(self, name: str, runnable: Runnable) -> None:
        self.name = name
        self.runnable = runnable

    def run(self):
        print(f"Running {self.name}")
        self.runnable.run()


class Retry(Runnable):
    def __init__(self, runnable: Runnable, nb_times: int) -> None:
        self.runnable = runnable
        self.max_retries = nb_times

    def run(self):
        retries = 0

        while True:
            try:
                self.runnable.run()
            except Exception as e:
                if retries >= self.max_retries:
                    raise e
                else:
                    print("An exception occured while running pipeline :")
                    print(traceback.format_exc())
                    retries += 1


class MultiThread(Runnable):
    def __init__(self, runnables: List[Runnable]) -> None:
        self.threads = [
            Thread(name=runnable.__class__.__name__, target=runnable.run)
            for runnable in runnables
        ]

    def run(self) -> None:
        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()


class MultiProcess(Runnable):
    def __init__(self, runnables: List[Runnable]) -> None:
        self.processes = [
            Process(name=runnable.__class__.__name__, target=runnable.run)
            for runnable in runnables
        ]

    def run(self) -> None:
        for process in self.processes:
            process.start()

        for process in self.processes:
            process.join()
