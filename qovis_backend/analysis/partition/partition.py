import abc
from typing import List

from common.summary_graph import SGraph


class Partition(abc.ABC):
    def __init__(self, strategy, sg_lst, k):
        self.strategy = strategy
        self.sg_lst: List[SGraph] = sg_lst
        self.k: int = k
        self.intervals: List[(int, int)] = []

    @abc.abstractmethod
    def execute(self):
        pass

    def get_intervals(self) -> List[(int, int)]:
        return self.intervals
