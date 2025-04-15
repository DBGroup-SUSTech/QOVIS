import itertools
import json
import random
import time
from math import ceil
from typing import Optional, Callable
from queue import PriorityQueue
from multiset import Multiset

from trans.algo.algo_status import AlgoStatus
from trans.plan.join_utils import JoinUtils
from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.join_like import JoinLike
from trans.plan.operator.proj_like import ProjLike
from trans.plan.plan_node import PlanNode
from trans.plan.query_plan import QueryPlan
from trans.plan.utils.fragment_set import Fragment2Set
from trans.plan.utils.plan_map import PlanMap
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.pred_infer_by_attrs import PredInferByAttrs
from trans.rule.constraint.impl.pred_infer_by_const import PredInferByConst
from trans.rule.constraint.impl.pred_merge import PredMerge
from trans.rule.constraint.impl.pred_split import PredSplit
from trans.rule.constraint.impl.pred_split_by_attrs import PredSplitByAttrs
from trans.rule.rule import Rule

from dataclasses import dataclass, field

from utils.disjoint_set import DisjointSet
from utils.graph import Graph


@dataclass(order=True)
class PrioritizedItem:
    priority: int   # f
    plan: QueryPlan = field(compare=False)

    def __init__(self, plan: QueryPlan, f: int):
        self.priority = f
        self.plan = plan


class TransPathSearcherAHP:
    def __init__(self, t_src: QueryPlan, t_dst: QueryPlan,
                 normal_rules: list[Rule], reorder_rules: list[Rule],
                 cache_path: str = '',
                 sample_rate: float = 0.001,
                 reorder_timeout: int = 5, normal_timeout: int = 20):
        self.t_src = t_src
        self.t_dst = t_dst
        self.rules = normal_rules
        self.reorder_rules = reorder_rules

        self.attempt_count = 0
        self.generated_plan_count = 0

        self.delta_head: list[str] = []
        # op names
        self.op_name_to_idx: dict[str, int] = {}    # op name -> op idx
        # table order
        self.order_idx = -1
        # 2-op fragment
        self.fragment2_lst: list[tuple[str, str]] = []
        self.fragment2_to_idx: dict[tuple[str, str], int] = {}  # fragment2 -> fragment2 idx
        # param change
        self.get_param_change_idx: Callable[[str], int] = None

        self.delta_groups: list[list[int]] = []     # index of d in delta_head
        self.delta_graphs: list[Graph] = []         # relation graph of delta item groups

        self.join_like_names: set[str] = set()
        self.max_rule_delta: list[int] = []                # max delta change for one rule
        self.rule_delta_list: list[list[int]] = []         # rule delta list

        # self.cache: list[tuple[int, QueryPlan, list[Rule]]] = []
        self.cache_path = cache_path
        self.sample_rate = sample_rate

        # time
        self.reorder_timeout = reorder_timeout
        self.normal_timeout = normal_timeout
        self.reorder_time = 0
        self.normal_time = 0
        self.status: AlgoStatus = AlgoStatus.INIT

    def precompute(self):
        join_like_types = JoinLike.get_all_concrete_subclass()
        self.join_like_names = set(map(lambda cls: cls().name, join_like_types))

        self.delta_head = []

        # compute delta_head
        # delta_head part 1: op # change
        op_name_set = set()
        for rule in self.rules:
            nodes = rule.src.collect_all()
            if rule.dst is not None:
                nodes = itertools.chain(nodes, rule.dst.collect_all())
            # process join
            op_name_set = op_name_set.union(map(self.get_name, nodes))
        op_names = list(op_name_set)
        op_names.sort()
        self.op_name_to_idx = {name: i for i, name in enumerate(op_names)}
        self.delta_head += op_names

        # delta_head part 2: join order.
        # self.order_idx = len(self.delta_head)
        # self.delta_head += ['JoinOrder']

        # delta_head part 3: 2-op fragment
        # (parent, children)
        self.fragment2_lst = [
            ('JoinLike', 'Filter'),
            ('Filter', 'JoinLike'),

            ('JoinLike', 'Project'),
            ('Project', 'JoinLike'),

            ('Project', 'Project'),
            ('Filter', 'Filter'),

            ('Project', 'Filter'),
            ('Filter', 'Project'),
        ]
        self.fragment2_to_idx = {fragment: i + len(self.delta_head)
                                 for i, fragment in enumerate(self.fragment2_lst)}
        self.delta_head += list(map(lambda t: t[0] + '-' + t[1], self.fragment2_lst))

        # delta_head part 4: parameter change
        self.delta_head += ['FilterPred', 'JoinPred', 'ProjectExprs']
        start_idx = len(self.delta_head) - 3

        def _get_param_change_idx(delta_name: str) -> int:
            if delta_name == 'FilterPred':
                return start_idx
            elif delta_name == 'JoinPred':
                return start_idx + 1
            elif delta_name == 'ProjectExprs':
                return start_idx + 2
            else:
                raise ValueError(f'unknown parameter change delta: {delta_name}')
        self.get_param_change_idx = _get_param_change_idx

        # compute rule_delta_list
        self.rule_delta_list = [[]] * len(self.rules)
        for rule_idx, rule in enumerate(self.rules):
            delta = self.compute_rule_delta(rule)
            self.rule_delta_list[rule_idx] = delta
        # print rule_delta_list as csv
        # print('rule' + '\t' + "\t".join(self.delta_head))
        # for rule_idx, delta in enumerate(self.rule_delta_list):
        #     print(self.rules[rule_idx].name + '\t' + "\t".join(map(str, delta)))

        # compute delta groups
        ds = DisjointSet(list(range(len(self.delta_head))))
        mtx = [[0] * len(self.delta_head) for _ in range(len(self.delta_head))]
        for delta in self.rule_delta_list:
            delta_idx_lst = [i for i, d in enumerate(delta) if d != 0]
            for i, j in zip(delta_idx_lst, delta_idx_lst[1:]):
                ds.union(i, j)
                # mtx[i][j] = 1
                # mtx[j][i] = 1
            for idx0 in range(len(delta_idx_lst)):
                for idx1 in range(idx0 + 1, len(delta_idx_lst)):
                    i, j = delta_idx_lst[idx0], delta_idx_lst[idx1]
                    mtx[i][j] = 1
                    mtx[j][i] = 1
        self.delta_groups = ds.get_groups()

        # # print delta groups
        # print('delta groups:')
        # for group in self.delta_groups:
        #     print([self.delta_head[i] for i in group])
        # print delta matrix
        # print('delta matrix:')
        # for i, row in enumerate(mtx):
        #     print(','.join(map(str, row)))

        self.delta_graphs = []
        for group in self.delta_groups:
            g = Graph(group)
            self.delta_graphs.append(g)
            for i in group:
                adj_row = mtx[i]
                for j, adj in enumerate(adj_row):
                    if adj != 0:
                        g.add_edge(i, j)
            # g.print_adj()
            # print(g.independent_sets)

        # compute max_rule_delta
        self.max_rule_delta = [0] * len(self.delta_head)
        for delta in self.rule_delta_list:
            for i, d in enumerate(delta):
                self.max_rule_delta[i] = max(self.max_rule_delta[i], d)

        # print(self.delta_head)

    def compute_delta(self, t0: PlanNode, t1: PlanNode) -> list[int]:
        delta = [0] * len(self.delta_head)

        # op num change
        mset0 = Multiset(map(self.get_name, t0.collect_all()))
        mset1 = Multiset(map(self.get_name, t1.collect_all()))
        for name in mset0.union(mset1).distinct_elements():
            if name not in self.op_name_to_idx:
                continue
            delta[self.op_name_to_idx[name]] = abs(mset0[name] - mset1[name])

        # join order change
        # swap_cnt = JoinUtils.get_min_join_order_swap_cnt(t0, t1)
        # delta[self.order_idx] = swap_cnt

        # 2-op fragment change
        fragment_set0 = Fragment2Set(self.fragment2_lst)
        for fragment in self.get_2_fragments(t0):
            fragment_set0.add(fragment)
        fragment_set1 = Fragment2Set(self.fragment2_lst)
        for fragment in self.get_2_fragments(t1):
            fragment_set1.add(fragment)
        for fragment in self.fragment2_lst:
            idx = self.fragment2_to_idx[fragment]
            delta[idx] = abs(fragment_set0.count(fragment) - fragment_set1.count(fragment))

        # parameter change
        # FilterPred
        filter_pred_set0 = Multiset()
        filter_pred_set1 = Multiset()
        # JoinPred
        join_pred_set0 = Multiset()
        join_pred_set1 = Multiset()
        # ProjectExprs
        project_exprs_set0 = Multiset()
        project_exprs_set1 = Multiset()

        for node in t0.collect_all():
            if issubclass(node.__class__, Filter):
                filter_pred_set0.add(node.pred.to_hash_str())
            elif issubclass(node.__class__, JoinLike):
                join_pred_set0.add(node.pred.to_hash_str())
            elif issubclass(node.__class__, ProjLike):
                project_exprs_set0.add(node.exprs.to_hash_str())

        for node in t1.collect_all():
            if issubclass(node.__class__, Filter):
                filter_pred_set1.add(node.pred.to_hash_str())
            elif issubclass(node.__class__, JoinLike):
                join_pred_set1.add(node.pred.to_hash_str())
            elif issubclass(node.__class__, ProjLike):
                project_exprs_set1.add(node.exprs.to_hash_str())

        delta[self.get_param_change_idx('FilterPred')] = len(filter_pred_set1 - filter_pred_set0)
        delta[self.get_param_change_idx('JoinPred')] = len(join_pred_set1 - join_pred_set0)
        delta[self.get_param_change_idx('ProjectExprs')] = len(project_exprs_set1 - project_exprs_set0)

        return delta

    def compute_rule_delta(self, rule: Rule) -> list[int]:
        t0, t1 = rule.src, rule.dst

        delta = [0] * len(self.delta_head)

        # op names
        mset0 = Multiset(map(self.get_name, t0.collect_all()))
        mset1 = Multiset(map(self.get_name, t1.collect_all()) if t1 is not None else [])
        for name in mset0.union(mset1).distinct_elements():
            if name not in self.op_name_to_idx:
                continue
            delta[self.op_name_to_idx[name]] = abs(mset0[name] - mset1[name])

        # join order
        # if t1 is not None:
        #     # rel_eq_constraints = list(filter(lambda c: isinstance(c, RelEq), rule.trans_constraints))
        #     # hard code for now
        #     if rule.name == 'ExchangeInnerJoinChildren':
        #         delta[self.order_idx] = 1
        #     elif rule.name == 'ReorderInnerJoin':
        #         delta[self.order_idx] = 1

        # 2-op fragment
        fragment_set0 = Fragment2Set(self.fragment2_lst)
        fragment_set0.add_all(self.get_2_fragments_for_pattern(t0))
        fragment_set1 = Fragment2Set(self.fragment2_lst)
        if t1 is not None:
            fragment_set1.add_all(self.get_2_fragments_for_pattern(t1))
        for fragment in self.fragment2_lst:
            idx = self.fragment2_to_idx[fragment]
            delta[idx] = abs(fragment_set0.count(fragment) - fragment_set1.count(fragment))

        # parameter change
        for c in rule.trans_constraints:
            if isinstance(c, PredInferByConst) or isinstance(c, PredInferByAttrs):
                name = self._get_owner_op_name(c.p1.owner)
                if name == 'Filter':
                    delta[self.get_param_change_idx('FilterPred')] += 1
                elif name == 'JoinLike':
                    delta[self.get_param_change_idx('JoinPred')] += 1
            elif isinstance(c, PredMerge):
                name = self._get_owner_op_name(c.p2.owner)
                if name == 'Filter':
                    delta[self.get_param_change_idx('FilterPred')] += 1
                elif name == 'JoinLike':
                    delta[self.get_param_change_idx('JoinPred')] += 1
            elif isinstance(c, PredSplit) or isinstance(c, PredSplitByAttrs):
                for p in [c.p1, c.p2]:
                    name = self._get_owner_op_name(p.owner)
                    if name == 'Filter':
                        delta[self.get_param_change_idx('FilterPred')] += 1
                    elif name == 'JoinLike':
                        delta[self.get_param_change_idx('JoinPred')] += 1
            elif isinstance(c, ExprsEq) and c.need_computation():
                name = self._get_owner_op_name(c.e1.owner)
                if name == 'Project':
                    delta[self.get_param_change_idx('ProjectExprs')] += 1

        return delta

    def _get_owner_op_name(self, owner: Optional[PlanNode]) -> str:
        if owner is None or not isinstance(owner, PlanNode):
            return ''
        return self.get_name(owner)

    def get_2_fragments_for_pattern(self, root: PlanNode) -> list[tuple[str, str]]:
        results = [(Fragment2Set.ANY, self.get_name(root))]
        for parent in root.collect_all():
            if parent.n_child == 0:
                continue
            # should have children
            if len(parent.children) == 0:
                # children not set
                for _ in range(parent.n_child):
                    results.append((self.get_name(parent), Fragment2Set.ANY))
            else:
                # children set
                for child in parent.children:
                    if child is None:
                        results.append((self.get_name(parent), Fragment2Set.ANY))
                    else:
                        results.append((self.get_name(parent), self.get_name(child)))
        return results

    def get_2_fragments(self, root: PlanNode) -> list[tuple[str, str]]:
        results = []
        for parent in root.collect_all():
            for child in parent.children:
                results.append((self.get_name(parent), self.get_name(child)))
        return results

    def get_name(self, op: PlanNode) -> str:
        name = op.name
        if name in self.join_like_names:
            return 'JoinLike'
        return name

    @staticmethod
    def hash_list(lst: list[int]) -> str:
        return ' '.join(map(str, lst))

    def execute(self) -> Optional[list[Rule]]:
        self.reorder_time = 0
        self.normal_time = 0

        result0 = self.search_reorder_transform_path(self.t_src)
        if result0 is None:
            print(f'reorder search time: {self.reorder_time}, status: {self.status}')
            self.status = AlgoStatus.FAILED
            return None
        tmp_plan, path0 = result0

        path1 = self.search_normal_transform_path(tmp_plan)
        print(f'normal search time: {self.normal_time}, status: {self.status}')
        if path1 is None:
            self.status = AlgoStatus.FAILED
            return None

        self.status = AlgoStatus.SUCCESS
        return path0 + path1

    def search_reorder_transform_path(self, start: QueryPlan) -> Optional[tuple[QueryPlan, list[Rule]]]:
        start_time = time.time()

        if start.has_same_struct(self.t_dst):
            self.reorder_time = time.time() - start_time
            self.status = AlgoStatus.SUCCESS
            return start, []

        src_f = JoinUtils.get_min_join_order_swap_cnt(start.root, self.t_dst.root)

        path_dict: PlanMap[list[Rule]] = PlanMap()
        open_q: PriorityQueue[PrioritizedItem] = PriorityQueue()
        open_set: PlanMap[None] = PlanMap()

        path_dict[start] = []
        open_q.put(PrioritizedItem(start, src_f))
        open_set[start] = None

        max_g = 0
        while True:
            if time.time() - start_time > self.reorder_timeout:
                self.status = AlgoStatus.TIMEOUT
                break

            if open_q.qsize() <= 0:
                self.status = AlgoStatus.FAILED
                break

            item = open_q.get()

            # f = item.priority
            t = item.plan
            t_path = path_dict[t]
            g = len(t_path) + 1
            if g > max_g:
                max_g = g
                self.generated_plan_count = len(path_dict)
                # print('g =', g, 'open_q.size =', open_q.qsize(),
                #       'attempt_count =', self.attempt_count,
                #       'generated_plan_count =', len(path_dict))
            for rule in self.reorder_rules:
                self.attempt_count += 1
                new_ts = rule.apply(t)
                for new_t in new_ts:
                    if new_t.has_same_struct(self.t_dst):
                        path = t_path + [rule]
                        # print('|path| =', len(path), 'open_q.size =', open_q.qsize(),
                        #       'attempt_count =', self.attempt_count,
                        #       'generated_plan_count =', len(path_dict))
                        self.reorder_time = time.time() - start_time
                        return new_t, path
                    if new_t in path_dict:
                        new_t_g = len(path_dict[new_t]) + 1
                        if new_t_g <= g:
                            continue
                    path_dict[new_t] = t_path + [rule]
                    if new_t not in open_set:
                        h = JoinUtils.get_min_join_order_swap_cnt(new_t.root, self.t_dst.root)
                        f = g + h
                        # add to open set
                        open_q.put(PrioritizedItem(new_t, f))
                        open_set[new_t] = None

        self.reorder_time = time.time() - start_time
        # no path found or timeout
        return None

    def search_normal_transform_path(self, start: QueryPlan) -> Optional[list[Rule]]:
        start_time = time.time()
        self.attempt_count = 0
        self.generated_plan_count = 0

        if start.semantically_equals(self.t_dst):
            self.normal_time = time.time() - start_time
            self.status = AlgoStatus.SUCCESS
            return []

        src_f = self.get_min_step_cnt(start, self.t_dst)

        # probe
        self.append_result(0, 0, start, [])
        self.append_result(0, 0, self.t_dst, [])

        path_dict: PlanMap[list[Rule]] = PlanMap()
        open_q: PriorityQueue[PrioritizedItem] = PriorityQueue()
        open_set: PlanMap[None] = PlanMap()

        path_dict[start] = []
        open_q.put(PrioritizedItem(start, src_f))
        open_set[start] = None

        max_g = 0
        while True:
            if time.time() - start_time > self.normal_timeout:
                self.status = AlgoStatus.TIMEOUT
                break

            if open_q.empty():
                self.status = AlgoStatus.FAILED
                break

            item = open_q.get()

            # f = item.priority
            t = item.plan
            t_path = path_dict[t]
            g = len(t_path) + 1
            if g > max_g:
                max_g = g
                self.generated_plan_count = len(path_dict)
                # print('g =', g, 'open_q.size =', open_q.qsize(),
                #       'attempt_count =', self.attempt_count,
                #       'generated_plan_count =', len(path_dict))
            for rule in self.rules:
                self.attempt_count += 1
                new_ts = rule.apply(t)
                for new_t in new_ts:
                    if new_t.semantically_equals(self.t_dst):
                        path = t_path + [rule]
                        # print('|path| =', len(path), 'open_q.size =', open_q.qsize(),
                        #       'attempt_count =', self.attempt_count,
                        #       'generated_plan_count =', len(path_dict))
                        self.normal_time = time.time() - start_time
                        return path
                    if new_t in path_dict:
                        new_t_g = len(path_dict[new_t]) + 1
                        if new_t_g <= g:
                            continue
                    path_dict[new_t] = t_path + [rule]
                    if new_t not in open_set:
                        h = self.get_min_step_cnt(new_t, self.t_dst)
                        f = g + h
                        # add to open set
                        open_q.put(PrioritizedItem(new_t, f))
                        open_set[new_t] = None

        self.normal_time = time.time() - start_time
        # no path found or timeout
        return None

    def get_min_step_cnt(self, t0: QueryPlan, t1: QueryPlan) -> int:
        """ H+ """
        delta = self.compute_delta(t0.root, t1.root)

        # H_i
        min_steps = [0] * len(delta)
        for idx in range(len(delta)):
            d, max_d = delta[idx], self.max_rule_delta[idx]
            if max_d == 0:
                if d != 0:
                    return 100000
                continue
            min_steps[idx] = ceil(d / max_d)

        total_step_cnt = 0
        for graph in self.delta_graphs:
            group_step_cnt = 0
            for ind_set in graph.independent_sets:
                step_cnt = sum(min_steps[idx] for idx in ind_set)
                group_step_cnt = max(group_step_cnt, step_cnt)
            total_step_cnt += group_step_cnt

        return total_step_cnt

    def get_delta_dist(self, t0: QueryPlan, t1: QueryPlan) -> int:
        """ H^ """
        delta = self.compute_delta(t0.root, t1.root)
        return sum(delta)

    def append_result(self, g: int, h: int, plan: QueryPlan, path: list[Rule]):
        if self.cache_path == '':
            return
        line = json.dumps([g, h, plan.dump(), list(map(lambda r: r.name, path))])
        with open(self.cache_path, 'a') as f:
            f.write(line + '\n')

    def get_time_cost(self):
        res = self.reorder_time + self.normal_time
        if res < 10 ** -6:
            return 0
        return res * 1000       # s -> ms

