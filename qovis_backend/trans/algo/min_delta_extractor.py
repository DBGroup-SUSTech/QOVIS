import itertools
import json
import random
import sys
import time
from math import ceil
from typing import Optional, Callable
from queue import PriorityQueue
from multiset import Multiset

from trans.plan.join_utils import JoinUtils
from trans.plan.operator.join_like import JoinLike
from trans.plan.plan_node import PlanNode
from trans.plan.query_plan import QueryPlan
from trans.plan.utils.fragment_set import Fragment2Set
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.pred_infer_by_const import PredInferByConst
from trans.rule.constraint.impl.pred_merge import PredMerge
from trans.rule.constraint.impl.pred_split import PredSplit
from trans.rule.rule import Rule

from dataclasses import dataclass, field

from utils.disjoint_set import DisjointSet
from utils.graph import Graph


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    plan: QueryPlan = field(compare=False)

    def __init__(self, priority: int, plan: QueryPlan):
        self.priority = priority
        self.plan = plan


class MinDeltaExtractor:
    def __init__(self, t_src: QueryPlan, t_dst: QueryPlan, rules: list[Rule], cache_path: str,
                 max_depth: int = 30, sample_rate: float = 0.001):
        self.t_src = t_src
        self.t_dst = t_dst
        self.rules = rules
        self.max_depth = max_depth

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

        # delta_head part 2: join order
        self.order_idx = len(self.delta_head)
        self.delta_head += ['JoinOrder']

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

        # compute max_rule_delta
        self.max_rule_delta = [0] * len(self.delta_head)
        for delta in self.rule_delta_list:
            for i, d in enumerate(delta):
                self.max_rule_delta[i] = max(self.max_rule_delta[i], d)

        print(self.delta_head)

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
        swap_cnt = JoinUtils.get_min_join_order_swap_cnt(t0, t1)
        delta[self.order_idx] = swap_cnt

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
            name = self.get_name(node)
            if name == 'Filter':
                filter_pred_set0.add(node.pred.to_hash_str())
            elif name == 'JoinLike':
                join_pred_set0.add(node.pred.to_hash_str())
            elif name == 'Project':
                project_exprs_set0.add(node.exprs.to_hash_str())

        for node in t1.collect_all():
            name = self.get_name(node)
            if name == 'Filter':
                filter_pred_set1.add(node.pred.to_hash_str())
            elif name == 'JoinLike':
                join_pred_set1.add(node.pred.to_hash_str())
            elif name == 'Project':
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
        if t1 is not None:
            # rel_eq_constraints = list(filter(lambda c: isinstance(c, RelEq), rule.trans_constraints))
            # hard code for now
            if rule.name == 'ExchangeInnerJoinChildren':
                delta[self.order_idx] = 1
            elif rule.name == 'ReorderInnerJoin':
                delta[self.order_idx] = 1

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
            if isinstance(c, PredInferByConst):
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
            elif isinstance(c, PredSplit):
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
        # results = [(Fragment2Set.ANY, self.get_name(root))]
        results = []
        for parent in root.collect_all():
            if parent.n_child == 0:
                continue
            # should have children
            if len(parent.children) == 0:
                # children not set
                pass
                # for _ in range(parent.n_child):
                #     results.append((self.get_name(parent), Fragment2Set.ANY))
            else:
                # children set
                for child in parent.children:
                    if child is None:
                        pass
                        # results.append((self.get_name(parent), Fragment2Set.ANY))
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
        self.attempt_count = 0
        self.generated_plan_count = 0

        if self.t_src.semantically_equals(self.t_dst):
            return []

        src_hash = self.t_src.to_hash_str()
        src_f = self.get_delta_dist(self.t_src, self.t_dst)

        # probe
        rand = random.Random(0)
        self.append_result(0, 0, self.t_src, [])
        self.append_result(0, 0, self.t_dst, [])

        path_dict: dict[str, list[Rule]] = {src_hash: []}
        g_dict = {src_hash: 0}
        open_q: PriorityQueue[PrioritizedItem] = PriorityQueue()
        open_q.put(PrioritizedItem(src_f, self.t_src))
        open_set: set[str] = {src_hash}
        max_g = 0
        # max_f = 0
        while not open_q.empty():
            item = open_q.get()
            # f = item.priority
            t = item.plan
            t_hash = t.to_hash_str()
            open_set.remove(t_hash)
            g = g_dict[t_hash] + 1
            for rule in self.rules:
                self.attempt_count += 1
                new_ts = rule.apply(t)
                for new_t in new_ts:
                    # g = g_dict[t_hash] + self.get_delta_dist(t, new_t)
                    if g > max_g:
                        max_g = g
                        print('g =', g, 'open_q.size =', open_q.qsize(),
                              'attempt_count =', self.attempt_count,
                              'generated_plan_count =', self.generated_plan_count)
                    if new_t.semantically_equals(self.t_dst):
                        path = path_dict[t_hash] + [rule]
                        print('|path| =', len(path), 'open_q.size =', open_q.qsize(),
                              'attempt_count =', self.attempt_count,
                              'generated_plan_count =', self.generated_plan_count)
                        return path
                    new_t_hash = new_t.to_hash_str()
                    if new_t_hash in g_dict:
                        if g_dict[new_t_hash] <= g:
                            continue
                    else:
                        self.generated_plan_count += 1
                    path_dict[new_t_hash] = path_dict[t_hash] + [rule]
                    g_dict[new_t_hash] = g
                    if new_t_hash not in open_set:
                        h = self.get_delta_dist(new_t, self.t_dst)
                        f = g + h
                        open_q.put(PrioritizedItem(f, new_t))
                        open_set.add(new_t_hash)

                        if rand.random() < self.sample_rate:
                            self.append_result(g, h, new_t, path_dict[new_t_hash])

        # no path found
        return None

    def get_delta_dist(self, t0: QueryPlan, t1: QueryPlan) -> int:
        """ H_delta """
        delta = self.compute_delta(t0.root, t1.root)
        return sum(delta)

    def append_result(self, g: int, h: int, plan: QueryPlan, path: list[Rule]):
        line = json.dumps([g, h, plan.dump(), list(map(lambda r: r.name, path))])
        with open(self.cache_path, 'a') as f:
            f.write(line + '\n')
