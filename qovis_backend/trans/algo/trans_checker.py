from typing import Optional

from trans.plan.query_plan import QueryPlan
from trans.rule.rule import Rule


class TransChecker:
    def __init__(self, t_src: QueryPlan, t_dst: QueryPlan, rule_seq: list[Rule],
                 match_index_list: list[Optional[int]] = None):
        self.t_src = t_src
        self.t_dst = t_dst
        self.rule_seq = rule_seq
        self.match_index_list = match_index_list

    def is_valid(self) -> bool:
        if self.t_src.semantically_equals(self.t_dst):
            return len(self.rule_seq) == 0

        cur_level: list[QueryPlan] = [self.t_src]
        mem = {self.t_src.to_hash_str()}
        for i, rule in enumerate(self.rule_seq):
            print('path', self.rule_seq[:i+1], 'plans', len(cur_level))
            if len(cur_level) == 0:
                return False
            next_level: list[QueryPlan] = []
            for t in cur_level:
                # apply the rule
                if self.match_index_list is not None and self.match_index_list[i] is not None:
                    m_idx = self.match_index_list[i]
                    trans_list = rule.apply_with_index(t, m_idx)
                else:
                    trans_list = rule.apply(t)
                # process generated plans
                for new_t in trans_list:
                    if new_t.to_hash_str() in mem:
                        continue
                    next_level.append(new_t)
                    mem.add(new_t.to_hash_str())
            cur_level = next_level

        for t in cur_level:
            if t.semantically_equals(self.t_dst):
                return True

        return False
