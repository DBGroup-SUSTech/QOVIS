import random
from typing import List

from analysis.algo.summary_algo import SummaryAlgo, ExtractStrategy, GenerateStrategy
from common.summary_graph import SGraph


class AlgoRandNoop(SummaryAlgo):
    def __init__(self, example_path):
        super().__init__(
            example_path,
            ExtractStrategy.RAND,
            GenerateStrategy.NOOP,
        )
        self.rand = random.Random(3407)

        self.sg_lst: List[SGraph] = []

    def _execute_algo(self):
        self.sg_lst = [SGraph.load_from_plan(p) for p in self.dg.plans]
        self.compute_encoding_cost()
        self.compute_loss()
        self.compute_result()

    def compute_encoding_cost(self):
        w1 = 1      # node encoding cost
        w2 = 0      # edge encoding cost

        cost = 0

        for sg in self.sg_lst:
            cost += w1 * len(sg.node_dict)
            cost += w2 * len(sg.edge_dict)

        self.cost = cost

    def compute_loss(self):
        self.loss = 0

    def compute_result(self):
        self.summary = {
            'sgList': [sg.dump() for sg in self.sg_lst],
        }

