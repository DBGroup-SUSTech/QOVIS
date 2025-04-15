import time
from typing import Tuple, Optional

from trans.algo.algo_status import AlgoStatus
from trans.plan.query_plan import QueryPlan
from trans.rule.rule import Rule


class TransPathSearcherBFS:
    """ BFS """

    def __init__(self, t_src: QueryPlan, t_dst: QueryPlan, rules: list[Rule], timeout: int = 20):
        self.t_src = t_src
        self.t_dst = t_dst
        self.rules = rules
        self.timeout = timeout

        self.time_cost = 0
        self.attempt_count = 0
        self.generated_plan_count = 0
        self.status: AlgoStatus = AlgoStatus.INIT

    def execute(self) -> Optional[list[Rule]]:
        self.time_cost = 0

        path = self.search_transform_path()
        print(f'search time: {self.time_cost}, status: {self.status}')
        if path is None:
            return None

        return path

    def search_transform_path(self) -> Optional[list[Rule]]:
        start_time = time.time()
        self.time_cost = 0

        self.attempt_count = 0
        self.generated_plan_count = 0

        if self.t_src.semantically_equals(self.t_dst):
            self.time_cost = time.time() - start_time
            self.status = AlgoStatus.SUCCESS
            return []

        q: list[Tuple[QueryPlan, list[Rule]]] = [(self.t_src, [])]
        mem = {self.t_src.to_hash_str()}
        while True:
            if len(q) == 0:
                self.status = AlgoStatus.FAILED
                break
            if time.time() - start_time > self.timeout:
                self.status = AlgoStatus.TIMEOUT
                break
            t, path = q.pop(0)
            for rule in self.rules:
                # print('try', [r.name for r in path] + [rule.name])
                self.attempt_count += 1
                trans_list = rule.apply(t)
                for new_t in trans_list:
                    if new_t.to_hash_str() in mem:
                        continue
                    new_path = path + [rule]
                    if new_t.semantically_equals(self.t_dst):
                        self.status = AlgoStatus.SUCCESS
                        self.time_cost = time.time() - start_time
                        self.generated_plan_count = len(mem)
                        return new_path
                    q.append((new_t, new_path))
                    mem.add(new_t.to_hash_str())

        self.time_cost = time.time() - start_time
        # no path found
        return None

    def get_time_cost(self):
        res = self.time_cost
        if res < 10 ** -6:
            return 0
        return res * 1000       # s -> ms
