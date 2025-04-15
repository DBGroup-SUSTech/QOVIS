# import random
# from typing import List
#
# from analysis.algo.summary_algo import SummaryAlgo, ExtractStrategy, GenerateStrategy
# from common.plan import Plan
# from common.summary_graph import SGraph
#
#
# class AlgoRandKeepAll(SummaryAlgo):
#     def __init__(self, example_path):
#         super().__init__(
#             example_path,
#             ExtractStrategy.RAND,
#             GenerateStrategy.NOOP,
#         )
#         self.rand = random.Random(3407)
#
#         self.sg_lst: List[SGraph] = []
#
#     def execute_algo(self):
#         self.sg_lst = [SGraph.load(p) for p in self.dg.plans]
#
#         # x = 22
#         # while True:
#         #
#         #     self.compute_intervals()
#         #
#         #     intervals = [(i, i + 1) for i in range(len(self.plans) - 1)]
#         #     self.intervals = [(0, x)] + intervals[x:]
#         #
#         #     self.compute_delta_lst()
#         #     self.compute_encoding_cost()
#         #     self.compute_loss()
#         #     self.compute_result()
#         #
#         #     if self.loss + self.cost != 775:
#         #         print(x)
#         #     break
#         #     x += 1
#
#         self.compute_intervals()
#         self.compute_delta_lst()
#         self.compute_encoding_cost()
#         self.compute_loss()
#         self.compute_result()
#
#     def compute_intervals(self):
#         n = len(self.plans)
#         separators = []
#         candidates = list(range(1, n - 2))
#         while len(separators) < self.k - 1:
#             idx = self.rand.randint(0, len(candidates) - 1)
#             separators.append(candidates[idx])
#             del candidates[idx]
#
#         separators.sort()
#         intervals = []
#         separators = [0] + separators + [n - 1]
#         for i in range(0, self.k):
#             intervals.append((separators[i], separators[i + 1]))
#
#         # intervals = [(i, i+1) for i in range(n-1)]
#
#         self.intervals = intervals
#
#     def compute_delta_lst(self):
#         delta_lst = self.delta_lst = []
#         for start, end in self.intervals:
#             plan1 = self.plans[start]
#             plan2 = self.plans[end]
#             delta_lst.append(self.compute_delta(plan1, plan2))
#
#     def compute_delta(self, plan1: Plan, plan2: Plan):
#         nodes1 = set(plan1.node_dict.keys())
#         nodes2 = set(plan2.node_dict.keys())
#         node_plus = nodes2 - nodes1
#         node_minus = nodes1 - nodes2
#
#         edges1 = set(plan1.edge_dict.keys())
#         edges2 = set(plan2.edge_dict.keys())
#         edge_plus = edges2 - edges1
#         edge_minus = edges1 - edges2
#
#         return node_plus, node_minus, edge_plus, edge_minus
#
#     def compute_encoding_cost(self):
#         w1 = 1      # node encoding cost
#         w2 = 1      # edge encoding cost
#
#         cost = 0
#
#         cost += w1 * len(self.plans[0].node_dict)
#         cost += w2 * len(self.plans[0].edge_dict)
#         for node_plus, node_minus, edge_plus, edge_minus in self.delta_lst:
#             cost += w1 * (len(node_plus) + len(node_minus))
#             cost += w2 * (len(edge_plus) + len(edge_minus))
#
#         self.cost = cost
#
#     def compute_loss(self):
#         w1 = 1      # node encoding cost
#         w2 = 1      # edge encoding cost
#
#         loss = 0
#
#         for interval, delta in zip(self.intervals, self.delta_lst):
#             start, end = interval
#
#             for plan_idx in range(start, end):
#                 plan1 = self.plans[plan_idx]
#                 plan2 = self.plans[plan_idx + 1]
#                 temp_delta = self.compute_delta(plan1, plan2)
#                 # nodes
#                 for i in [0, 1]:
#                     diff_set = temp_delta[i] - delta[i]
#                     loss += w1 * len(diff_set)
#                 # edges
#                 for i in [2, 3]:
#                     diff_set = temp_delta[i] - delta[i]
#                     loss += w2 * len(diff_set)
#
#         self.loss = loss
#
#     def compute_result(self):
#         summary = self.summary = []
#         for interval, delta in zip(self.intervals, self.delta_lst):
#             causes = [c['eid'] for c in self.causes[interval[0]:interval[1]]]
#             edgePlus = list(delta[2])
#             edgeMinus = list(delta[3])
#             edgePlus.sort()
#             edgeMinus.sort()
#             summary.append({
#                 'interval': interval,
#                 'plans': [self.plans[i].plan_id for i in interval],
#                 'causes': causes,
#                 'delta': {
#                     'nodePlus': list(delta[0]),
#                     'nodeMinus': list(delta[1]),
#                     'edgePlus': edgePlus,
#                     'edgeMinus': edgeMinus,
#                 }
#             })
#
