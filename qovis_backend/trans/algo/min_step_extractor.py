import itertools
import sys
import time
from typing import Optional
from queue import PriorityQueue

from trans.plan.join_utils import JoinUtils
from trans.plan.operator.join_like import JoinLike
from trans.plan.plan_node import PlanNode
from trans.plan.query_plan import QueryPlan
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

from dataclasses import dataclass, field


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    plan: QueryPlan = field(compare=False)

    def __init__(self, priority: int, plan: QueryPlan):
        self.priority = priority
        self.plan = plan


class MinStepExtractor:
    def __init__(self, t_src: QueryPlan, t_dst: QueryPlan, rules: list[Rule], max_depth: int = 30):
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

        self.join_like_names: set[str] = set()
        self.rule_name_to_id: dict[str, int] = {}          # rule name -> rule id
        self.delta_dict: dict[str, int] = {}        # hash_list(delta) -> min step count

    def precompute(self):
        # compute rule id
        for i, rule in enumerate(self.rules):
            self.rule_name_to_id[rule.name] = i

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
        self.order_idx = len(op_names)
        self.delta_head += ['JoinOrder']

        # delta_head part 3: op position change
        # self.delta_head += ['FilterPos', 'ProjectPos']

        # compute delta_dict
        self.delta_dict = {
            self.hash_list([0] * len(self.delta_head)): 0
        }
        rule_delta_list: list[list[int]] = [[]] * len(self.rules)
        l0: list[tuple[list[int], list[int]]] = []
        l1 = []
        for rule in self.rules:
            # count different node types
            delta = self.compute_rule_delta(rule)
            if any(i != 0 for i in delta):
                # not all zero, update dict
                self.delta_dict[self.hash_list(delta)] = 1

            rule_id = self.rule_name_to_id[rule.name]
            l0.append(([rule_id], delta))
            rule_delta_list[rule_id] = delta
        # print rule_delta_list as csv
        print('rule' + '\t' + "\t".join(self.delta_head))
        for rule_id, delta in enumerate(rule_delta_list):
            print(self.rules[rule_id].name + '\t' + "\t".join(map(str, delta)))

        print('compute delta_dict. max_depth =', self.max_depth)
        start_time = time.time()
        for d in range(2, self.max_depth + 1):
            # print('compute delta_dict', d)
            for rule_id_list, delta in l0:
                i = max(rule_id_list)
                for j in range(i, len(self.rules)):
                    rule_delta = rule_delta_list[j]
                    new_delta = [p + q for p, q in zip(delta, rule_delta)]

                    delta_hash = self.hash_list(new_delta)
                    if delta_hash in self.delta_dict:
                        continue    # must <= d

                    # insert into reference dict
                    self.delta_dict[delta_hash] = d
                    # update next level
                    new_rule_id_list = rule_id_list + [j]
                    l1.append((new_rule_id_list, new_delta))

            l0 = l1
            l1 = []
        print('compute delta_dict done. time:', time.time() - start_time)

        print(self.delta_head)
        print('delta_dict size:', sys.getsizeof(self.delta_dict), 'bytes')

    def compute_delta(self, t0: PlanNode, t1: PlanNode) -> list[int]:
        delta = [0] * len(self.delta_head)

        # op names
        for node in t0.collect_all():
            name = self.get_name(node)
            if name not in self.op_name_to_idx:
                continue
            delta[self.op_name_to_idx[name]] -= 1
        for node in t1.collect_all():
            name = self.get_name(node)
            if name not in self.op_name_to_idx:
                continue
            delta[self.op_name_to_idx[name]] += 1

        swap_cnt = JoinUtils.get_min_join_order_swap_cnt(t0, t1)
        delta[self.order_idx] = swap_cnt

        return delta

    def compute_rule_delta(self, rule: Rule) -> list[int]:
        t0, t1 = rule.src, rule.dst

        delta = [0] * len(self.delta_head)

        # op names
        for node in t0.collect_all():
            name = self.get_name(node)
            if name not in self.op_name_to_idx:
                continue
            delta[self.op_name_to_idx[name]] -= 1
        if t1 is not None:
            for node in t1.collect_all():
                name = self.get_name(node)
                if name not in self.op_name_to_idx:
                    continue
                delta[self.op_name_to_idx[name]] += 1

        # join order
        if t1 is not None:
            # rel_eq_constraints = list(filter(lambda c: isinstance(c, RelEq), rule.trans_constraints))
            # hard code for now
            if rule.name == 'ExchangeInnerJoinChildren':
                delta[self.order_idx] = 1
            elif rule.name == 'ReorderInnerJoin':
                delta[self.order_idx] = 1

        return delta

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
        src_f = self.get_min_step_cnt(self.t_src, self.t_dst)

        path_dict: dict[str, list[Rule]] = {src_hash: []}
        g_dict = {src_hash: 0}
        open_q: PriorityQueue[PrioritizedItem] = PriorityQueue()
        open_q.put(PrioritizedItem(src_f, self.t_src))
        open_set: set[str] = {src_hash}
        max_g = 0
        while not open_q.empty():
            t = open_q.get().plan
            t_hash = t.to_hash_str()
            open_set.remove(t_hash)
            g = g_dict[t_hash] + 1
            if g > max_g:
                max_g = g
                print('g =', g, 'open_q.size =', open_q.qsize(),
                      'attempt_count =', self.attempt_count,
                      'generated_plan_count =', self.generated_plan_count)
            for rule in self.rules:
                self.attempt_count += 1
                new_ts = rule.apply(t)
                for new_t in new_ts:
                    if new_t.semantically_equals(self.t_dst):
                        print('g =', g, 'open_q.size =', open_q.qsize(),
                              'attempt_count =', self.attempt_count,
                              'generated_plan_count =', self.generated_plan_count)
                        return path_dict[t_hash] + [rule]
                    new_t_hash = new_t.to_hash_str()
                    if new_t_hash in g_dict and g_dict[new_t_hash] <= g:
                        continue
                    self.generated_plan_count += 1
                    path_dict[new_t_hash] = path_dict[t_hash] + [rule]
                    g_dict[new_t_hash] = g
                    if new_t_hash not in open_set:
                        f = g + self.get_min_step_cnt(new_t, self.t_dst)
                        open_q.put(PrioritizedItem(f, new_t))
                        open_set.add(new_t_hash)

        # no path found
        return None

    def get_min_step_cnt(self, t0: QueryPlan, t1: QueryPlan) -> int:
        delta = self.compute_delta(t0.root, t1.root)
        delta_hash = self.hash_list(delta)
        if delta_hash not in self.delta_dict:
            return self.max_depth + 1
        return self.delta_dict[delta_hash]
