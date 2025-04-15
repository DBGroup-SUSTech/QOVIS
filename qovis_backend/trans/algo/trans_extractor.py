from typing import Tuple, Optional

from trans.plan.query_plan import QueryPlan
from trans.rule.rule import Rule


class TransExtractor:
    def __init__(self, t_src: QueryPlan, t_dst: QueryPlan, rules: list[Rule], max_depth: int = 20):
        self.t_src = t_src
        self.t_dst = t_dst
        self.rules = rules
        self.max_depth = max_depth

        self.attempt_count = 0
        self.generated_plan_count = 0

    def execute(self) -> Optional[list[Rule]]:
        self.attempt_count = 0
        self.generated_plan_count = 0

        if self.t_src.semantically_equals(self.t_dst):
            return []

        q: list[Tuple[QueryPlan, list[Rule]]] = [(self.t_src, [])]
        mem = {self.t_src.to_hash_str()}
        max_depth = self.max_depth
        while len(q) > 0:
            t, path = q.pop(0)
            if len(path) > max_depth:
                continue
            for rule in self.rules:
                # print('try', [r.name for r in path] + [rule.name])
                self.attempt_count += 1
                trans_list = rule.apply(t)
                for new_t in trans_list:
                    if new_t.to_hash_str() in mem:
                        continue
                    self.generated_plan_count += 1
                    new_path = path + [rule]
                    if new_t.semantically_equals(self.t_dst):
                        return new_path
                    q.append((new_t, new_path))
                    mem.add(new_t.to_hash_str())

        # no path found
        return None
