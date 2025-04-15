import random
from typing import List, Dict, Set

from analysis.algo.summary_algo import SummaryAlgo, ExtractStrategy, GenerateStrategy
from common.plan import PlanNode, Plan
from common.summary_graph import SGraph
from utils.data_structure import is_same_lst


class AlgoRandStruct(SummaryAlgo):
    def __init__(self, example_path):
        super().__init__(
            example_path,
            ExtractStrategy.RAND,
            GenerateStrategy.STRUCT,
        )
        self.rand = random.Random(3407)

        self.sg_lst: List[SGraph] = []
        self.intervals: List[(int, int)] = []
        # dict: sg node vid -> eff
        self.eff_lst: List[Dict[int, bool]] = []
        self.key_lst: List[Dict[int, bool]] = []
        self.important_set: Set[int] = set()

    def _execute_algo(self):
        self.compute_intervals()
        self.compute_semantic_blocks()
        self.compute_node_effectiveness()
        self.compute_importance()

        self.compute_encoding_cost()
        self.compute_loss()
        self.compute_result()

    def compute_intervals(self):
        n = len(self.dg.plans)

        # separators = []
        # for i in range(1, n - 2, 2):
        #     type0 = self.dg.plans[i].meta.type
        #     type1 = self.dg.plans[i + 1].meta.type
        #     if type0 != type1:
        #         separators.append(i + 1)

        separators = []
        for i in range(len(self.dg.plans)):
            plan = self.dg.plans[i]
            if plan.pid in [9, 13, 37, 47, 63, 75]:
                separators.append(i)

        separators.sort()
        intervals = []
        separators = [0] + separators + [n - 1]
        for i in range(0, len(separators) - 1):
            intervals.append((separators[i], separators[i + 1]))

        self.intervals = intervals

    def compute_semantic_blocks(self):
        nodes_mtx: List[List[List[PlanNode]]] = []
        for p in self.dg.plans:
            nodes_lst = self.extract_structure(p)
            nodes_mtx.append(nodes_lst)

        # check
        for i, nodes_lst in enumerate(nodes_mtx):
            assert sum([len(nodes) for nodes in nodes_lst]) == len(self.dg.plans[i].node_dict)

        sg_lst = []
        for i, nodes_lst in enumerate(nodes_mtx):
            sg = SGraph()

            for nodes in nodes_lst:
                snode = sg.add_node()
                snode.plan_nodes = nodes
            # hardcode for query1
            sg.add_edge(sg.node_dict[1], sg.node_dict[0])
            sg.add_edge(sg.node_dict[2], sg.node_dict[1])
            sg.add_edge(sg.node_dict[3], sg.node_dict[1])

            sg.plan = self.dg.plans[i]

            sg_lst.append(sg)

        self.sg_lst = sg_lst

    def extract_structure(self, plan: Plan):
        # edge relation is hardcode by position
        nodes_lst = [[]] * 4

        # find join opt
        join_node = None
        for node in plan.node_dict.values():
            if len(node.providers) > 1:
                join_node = node
                break
        assert join_node is not None
        merge_group_types = ['Join', 'SortMergeJoin', 'BroadcastHashJoin',
                             'Project', 'Filter', 'Sort', 'ShuffleExchange',
                             'BroadcastExchange', 'AQEShuffleRead', 'InputAdapter']
        join_group = []

        # collect up
        contain_filter = False
        tmp = join_node
        while tmp.name in merge_group_types:
            # project and filter can't occur at the same time
            if contain_filter and tmp.name == 'Project':
                break
            contain_filter = tmp.name == 'Filter'

            join_group.append(tmp)
            if len(tmp.consumers) == 0:
                break
            tmp = tmp.consumers[0]

        # collect down
        tmp_groups = [v for v in join_node.providers]
        while len(tmp_groups) != 0:
            next_groups = []
            for tmp in tmp_groups:
                if tmp.name not in merge_group_types:
                    continue
                join_group.append(tmp)
                for p in tmp.providers:
                    next_groups.append(p)
            tmp_groups = next_groups

        nodes_lst[1] = join_group

        # collect group0
        group = []
        tmp = plan.root
        while tmp.name not in merge_group_types or (contain_filter and tmp.name == 'Project'):
            group.append(tmp)
            tmp = tmp.providers[0]
        nodes_lst[0] = group

        # collect group2
        group = []
        tmp = join_node.providers[0]
        while tmp.name in merge_group_types:
            if len(tmp.providers) == 0:
                tmp = None  # no more node
                break
            tmp = tmp.providers[0]
        while tmp is not None:
            group.append(tmp)
            if len(tmp.providers) == 0:
                break
            tmp = tmp.providers[0]
        nodes_lst[2] = group

        # collect group3
        group = []
        tmp = join_node.providers[1]
        while tmp.name in merge_group_types:
            if len(tmp.providers) == 0:
                tmp = None  # no more node
                break
            tmp = tmp.providers[0]
        while tmp is not None:
            group.append(tmp)
            if len(tmp.providers) == 0:
                break
            tmp = tmp.providers[0]
        nodes_lst[3] = group

        return nodes_lst

    def compute_node_effectiveness(self):
        interval_start_set = set([t[0] for t in self.intervals])

        eff_lst = [{j: True for j in range(4)}]
        for i in range(len(self.sg_lst) - 1):
            sg0 = self.sg_lst[i]
            sg1 = self.sg_lst[i + 1]
            eff_dict = {}
            for j in range(4):      # hardcode
                v0 = sg0.node_dict[j]
                v1 = sg1.node_dict[j]
                eff_dict[j] = i + 1 in interval_start_set or \
                              not is_same_lst(v0.plan_nodes, v1.plan_nodes, lambda v: v.vid)
            eff_lst.append(eff_dict)
        self.eff_lst = eff_lst

        key_lst = [{j: True for j in range(4)}]
        for i in range(len(self.sg_lst) - 1):
            eff_dict0 = eff_lst[i]
            eff_dict1 = eff_lst[i + 1]
            key_dict = {}
            for j in range(4):  # hardcode
                key_dict[j] = eff_dict0[j] != eff_dict1[j]
            key_lst.append(key_dict)
        self.key_lst = key_lst

        # # first-last strategy
        # for start, end in self.intervals:
        #     for node_idx in range(4):
        #         first, last = -1, -1
        #         # find last one
        #         ptr = end
        #         while ptr > start:
        #             if eff_lst[ptr][node_idx]:
        #                 last = ptr
        #                 break
        #             ptr -= 1
        #         # set all other entity be ineffective
        #         for i in range(start + 1, end + 1):
        #             eff_lst[i][node_idx] = last == i

    def compute_importance(self):
        name_set = {'ColumnPruning', 'PushDownPredicates',
                    'ObjectSerializerPruning', 'RemoveNoopOperators', 'ReorderJoin',
                    'InferFiltersFromConstrains', 'CollapseProject', 'SparkStrategies$JoinSelection'}
        for i, p in enumerate(self.dg.plans):
            if any([name in p.meta.name for name in name_set]):
                self.important_set.add(i)

    def compute_encoding_cost(self):
        cost = 0

        for sg, eff_dict in zip(self.sg_lst, self.eff_lst):
            for i in range(4):
                node = sg.node_dict[i]
                is_eff = eff_dict[i]
                cost += len(node.plan_nodes) if is_eff else 0

        self.cost = cost

    def compute_loss(self):
        loss = 0

        for sg, key_dict, eff_dict in zip(self.sg_lst, self.key_lst, self.eff_lst):
            for i in range(4):
                node = sg.node_dict[i]
                is_key = key_dict[i]
                is_eff = eff_dict[i]
                loss += len(node.plan_nodes) if not is_key and is_eff else 0

        self.loss = 0

    def compute_result(self):
        self.summary = {
            'sgList': [sg.dump() for sg in self.sg_lst],
            'effList': self.eff_lst,
            'keyList': self.key_lst,
            'impList': list(self.important_set),
            'intervals': self.intervals,
        }



