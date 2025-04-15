import random
from typing import List, Callable, Dict

from analysis.cost.cost import edit_dist, label_group_cost, generate_subgraphs, compute_delta
from analysis.algo.summary_algo import SummaryAlgo, ExtractStrategy, GenerateStrategy
from common.plan import PlanNode, Plan
from common.sketch_graph import SGraph
from utils.data_structure import is_same_lst


class AlgoKeepAllTimelineCost(SummaryAlgo):
    def __init__(self, example_path):
        super().__init__(
            example_path,
            ExtractStrategy.KEEP_ALL,
            GenerateStrategy.TIMELINE_COST,
        )
        self.rand = random.Random(3407)

        self.node2delta_lst = {}

        self.sketch: SGraph = SGraph()
        self.intervals: List[(int, int)] = []
        self.cost_lst = []
        self.loss_lst = []

    def _execute_algo(self):
        self.compute_semantic_blocks()
        self.compute_intervals()
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

    def compute_intervals(self):
        n = self.sketch.seq_cnt

        intervals = [(i, i+1) for i in range(n-1)]

        self.intervals = intervals

    def compute_node_effectiveness(self):
        for node in self.sketch.nodes():
            eff_lst = [True]
            structure_seq = node.structure_seq
            for i in range(len(structure_seq) - 1):
                s0 = structure_seq[i]
                s1 = structure_seq[i + 1]
                eff = not is_same_lst(s0, s1, lambda v: v.vid)
                eff_lst.append(eff)
            node.eff_lst = eff_lst

        # first-last strategy
        for start, end in self.intervals:
            for node in self.sketch.nodes():
                first, last = -1, -1
                # find last one
                ptr = end
                while ptr > start:
                    if node.eff_lst[ptr]:
                        last = ptr
                        break
                    ptr -= 1
                # set all other entity be ineffective
                for i in range(start + 1, end + 1):
                    node.eff_lst[i] = last == i

                assert len(list(filter(lambda x: x, node.eff_lst[start + 1: end + 1]))) <= 2

    def compute_encoding_cost(self):
        cost_lst = [0, 0]
        coe_lst = [1, 0.2]

        eff_structs_dict: Dict[int, List[List[PlanNode]]] = {}
        for node in self.sketch.nodes():
            structures = []
            for struct, is_eff in zip(node.structure_seq, node.eff_lst):
                if is_eff:
                    sorted_struct = self.sort_struct(struct)
                    structures.append(sorted_struct)
            eff_structs_dict[node.vid] = structures

        # vis cost
        cost = 0
        for node in self.sketch.nodes():
            for structs in eff_structs_dict[node.vid]:
                cost += len(structs)
        cost_lst[0] = cost

        # label group
        cost = 0
        for node in self.sketch.nodes():
            labels_lst = []
            for plan, is_eff in zip(self.dg.plans, node.eff_lst):
                labels_lst.append(plan.meta.get_labels())
                if not is_eff:
                    continue
                cost += label_group_cost(labels_lst)
                labels_lst = []
        cost_lst[1] = cost

        print(cost_lst)
        self.cost_lst = cost_lst

        self.cost = sum([coe * c for coe, c in zip(coe_lst, cost_lst)])

    def sort_struct(self, struct: List[PlanNode]) -> List[PlanNode]:
        node_set = set(struct)

        # find root
        root = struct[0]
        while len(root.consumers) != 0 and root.consumers[0] in node_set:
            root = root.consumers[0]

        new_s = []

        def dfs(v: PlanNode):
            if v in node_set:
                new_s.append(v)
            else:
                return
            for p in v.providers:
                dfs(p)

        dfs(root)

        return new_s

    def compute_loss(self):
        loss_lst = [0, 0, 0]
        coe_lst = [1, 1, 1]

        eff_structs_dict: Dict[int, List[List[PlanNode]]] = {}
        for node in self.sketch.nodes():
            structures = []
            for struct, is_eff in zip(node.structure_seq, node.eff_lst):
                if is_eff:
                    sorted_struct = self.sort_struct(struct)
                    structures.append(sorted_struct)
            eff_structs_dict[node.vid] = structures

        # vis element loss
        loss = 0
        for node in self.sketch.nodes():
            structs = node.structure_seq
            struct_lst = [structs[0]]
            for s, is_eff in zip(structs[1:], node.eff_lst[1:]):
                struct_lst.append(s)
                if not is_eff:
                    continue
                node_plus, node_minus = compute_delta(struct_lst[0], struct_lst[-1])
                for i in range(len(struct_lst) - 1):
                    s0 = struct_lst[i]
                    s1 = struct_lst[i + 1]
                    node_plus_tmp, node_minus_tmp = compute_delta(s0, s1)
                    loss += len(node_plus_tmp - node_plus)
                    loss += len(node_minus_tmp - node_minus)
                struct_lst = [s]
        loss_lst[0] = loss

        # semantic change loss
        loss = 0
        lst0, lst1 = [], []
        for node in self.sketch.nodes():
            structs = node.structure_seq
            eff_structs = eff_structs_dict[node.vid]
            for i in range(len(eff_structs) - 1):
                loss -= edit_dist(eff_structs[i], eff_structs[i + 1])
                lst0.append(edit_dist(eff_structs[i], eff_structs[i + 1]))
            for i in range(len(structs) - 1):
                loss += edit_dist(structs[i], structs[i + 1])
                lst1.append(edit_dist(structs[i], structs[i + 1]))
        loss_lst[1] = loss

        # structure change loss
        loss = 0
        for node in self.sketch.nodes():
            subgraph_sets = [generate_subgraphs(s) for s in node.structure_seq]
            ss_lst = [subgraph_sets[0]]
            for ss, is_eff in zip(subgraph_sets[1:], node.eff_lst[1:]):
                ss_lst.append(ss)
                if not is_eff:
                    continue
                s_plus = ss_lst[-1] - ss_lst[0]
                s_minus = ss_lst[0] - ss_lst[-1]
                for i in range(len(ss_lst) - 1):
                    s0 = ss_lst[i]
                    s1 = ss_lst[i + 1]
                    s_plus_tmp, s_minus_tmp = s1 - s0, s0 - s1
                    loss += len(s_plus_tmp - s_plus)
                    loss += len(s_minus_tmp - s_minus)
                ss_lst = [ss]
        loss_lst[2] = loss

        print(loss_lst)
        self.loss_lst = loss_lst

        self.loss = sum([coe * c for coe, c in zip(coe_lst, loss_lst)])

    def compute_result(self):
        self.summary = {
            'sketch': self.sketch.dump(),
            'intervals': self.intervals,
        }



