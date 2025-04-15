import random
from typing import List, Dict

from analysis.algo.summary_algo import SummaryAlgo, ExtractStrategy, GenerateStrategy
from common.plan import PlanNode, Plan
from common.sketch_graph import SGraph
from utils.data_structure import is_same_lst


class AlgoRandTimeline(SummaryAlgo):
    def __init__(self, example_path):
        super().__init__(
            example_path,
            ExtractStrategy.RAND,
            GenerateStrategy.TIMELINE,
        )
        self.rand = random.Random(3407)

        self.sketch: SGraph = SGraph()
        self.intervals: List[(int, int)] = []

    def _execute_algo(self):
        self.compute_semantic_blocks()
        self.compute_node_effectiveness()

        self.compute_encoding_cost()
        self.compute_loss()
        self.compute_result()

    def compute_semantic_blocks(self):
        structures_lst: List[List[List[PlanNode]]] = []
        for p in self.dg.plans:
            structures = self.extract_structure(p)
            structures_lst.append(structures)

        # check
        for i, structures in enumerate(structures_lst):
            assert sum([len(nodes) for nodes in structures]) == len(self.dg.plans[i].node_dict)

        blocks_cnt = len(structures_lst[0])
        assert all([len(s) == blocks_cnt for s in structures_lst])

        # hardcode
        top_group = self.sketch.add_node()
        top_group.structure_seq = [structures[1] for structures in structures_lst]
        top_group.type = 'reduce'
        join_group = self.sketch.add_node()
        join_group.structure_seq = [structures[0] for structures in structures_lst]
        join_group.type = 'join'
        self.sketch.add_edge(join_group, top_group)

        # assume all len(structures) are same

        for i in range(2, len(structures_lst[0])):
            input_group = self.sketch.add_node()
            input_group.structure_seq = [structures[i] for structures in structures_lst]
            input_group.type = 'fetch'
            self.sketch.add_edge(input_group, join_group)

        self.sketch.seq_cnt = len(top_group.structure_seq)

    def extract_structure(self, plan: Plan):
        # edge relation is hardcode by position
        structures = []

        # find join opt
        join_node = None
        for node in plan.node_dict.values():
            if len(node.providers) > 1:
                join_node = node
                break
        assert join_node is not None
        merge_group_types = {'Join', 'SortMergeJoin', 'BroadcastHashJoin',
                             'Project', 'Filter', 'Sort', 'ShuffleExchange',
                             'BroadcastExchange', 'AQEShuffleRead', 'InputAdapter'}
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

        structures.append(join_group)

        # collect group0
        group = []
        tmp = plan.root
        while tmp.name not in merge_group_types or (contain_filter and tmp.name == 'Project'):
            group.append(tmp)
            tmp = tmp.providers[0]
        structures.append(group)

        # collect other groups
        candidates = []

        def dfs(v: PlanNode):
            if v is None:
                return
            if v.name in merge_group_types:
                for p in v.providers:
                    dfs(p)
            else:
                candidates.append(v)

        dfs(join_node)

        for c in candidates:
            group = []
            tmp = c
            while tmp is not None:
                group.append(tmp)
                if len(tmp.providers) == 0:
                    break
                assert len(tmp.providers) == 1
                tmp = tmp.providers[0]
            structures.append(group)

        return structures

    def compute_node_effectiveness(self):
        # interval_start_set = {t[0] for t in self.intervals}
        interval_start_set = set()

        for node in self.sketch.nodes():
            eff_lst = [True]
            structure_seq = node.structure_seq
            for i in range(len(structure_seq) - 1):
                s0 = structure_seq[i]
                s1 = structure_seq[i + 1]
                eff = i + 1 in interval_start_set or \
                      not is_same_lst(s0, s1, lambda v: v.vid)
                eff_lst.append(eff)
            node.eff_lst = eff_lst

    def compute_encoding_cost(self):
        cost = 0
        for node in self.sketch.nodes():
            for s, is_eff in zip(node.structure_seq, node.eff_lst):
                cost += len(s) if is_eff else 0
        self.cost = cost

    def compute_loss(self):
        loss = 0
        self.loss = loss

    def compute_result(self):
        self.summary = {
            'sketch': self.sketch.dump(),
            'intervals': self.intervals,
        }



