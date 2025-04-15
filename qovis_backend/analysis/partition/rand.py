import random

from analysis.partition.partition import Partition


class Rand(Partition):
    def __init__(self, sg_lst, k):
        super().__init__('rand', sg_lst, k)
        self.rand = random.Random(3407)

    def execute(self):
        n = len(self.sg_lst)
        separators = []
        candidates = list(range(1, n - 2))
        while len(separators) < self.k - 1:
            idx = self.rand.randint(0, len(candidates) - 1)
            separators.append(candidates[idx])
            del candidates[idx]

        separators.sort()
        intervals = []
        separators = [0] + separators + [n - 1]
        for i in range(0, self.k):
            intervals.append((separators[i], separators[i + 1]))

        # intervals = [(i, i+1) for i in range(n-1)]

        self.intervals = intervals
