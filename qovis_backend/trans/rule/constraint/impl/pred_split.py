import copy

from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


# deprecated
class PredSplit(TransConstraint):
    def __init__(self, p0: Predicate, p1: Predicate, p2: Predicate):
        super().__init__()
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.split_at = 1

    # v1

    # def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
    #     p0 = target_match.get_target_param(self.p0)
    #     p1 = repl_match.get_target_param(self.p1)
    #     p2 = repl_match.get_target_param(self.p2)
    #
    #     exprs0 = p0.expr_list[:self.split_at]
    #     exprs1 = p0.expr_list[self.split_at:]
    #
    #     p1.init_from_expr_list(exprs0)
    #     p2.init_from_expr_list(exprs1)
    #
    #     return [repl_match]

    # v2: random split

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        p0 = target_match.get_target_param(self.p0)
        exprs = p0.expr_list

        repl_matches = []
        splits = self.split_exprs(exprs)
        for exprs0, exprs1 in splits:
            repl_match_copy = copy.deepcopy(repl_match)
            p1 = repl_match_copy.get_target_param(self.p1)
            p2 = repl_match_copy.get_target_param(self.p2)
            p1.init_from_expr_list(exprs0)
            p2.init_from_expr_list(exprs1)
            repl_matches.append(repl_match_copy)

        return repl_matches

    @classmethod
    def split_exprs(cls, exprs: list[str]) -> list[tuple[list[str], list[str]]]:
        # def _find(f, lst):
        #     for i in range(len(lst)):
        #         if f(lst[i]):
        #             return i
        #     return None

        exprs = list(set(exprs))
        splits = []
        for i in range(2 ** len(exprs)):
            groups = ([], [])
            for j in range(len(exprs)):
                groups[(i >> j) & 1].append(exprs[j])
            if len(groups[0]) > 0 and len(groups[1]) > 0:
                splits.append(groups)
                splits.append(groups[::-1])

        # str_list = [(groups[0], groups[1]) for groups in splits]

        # idx = _find(lambda g: set(g[1]) == {'lo_partkey#21 = p_partkey#214', '(p_mfgr#216 = \"MFGR#1\") OR (p_mfgr#216 = \"MFGR#2\")'}, str_list)
        # if idx is not None:
        #     return [splits[idx]]
        #
        # idx = _find(lambda g: set(g[1]) == {'lo_suppkey#22 = s_suppkey#112', 's_region#117 = \"AMERICA\"'}, str_list)
        # if idx is not None:
        #     return [splits[idx]]

        return splits

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        return []

    # v3: split by position

    # def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
    #     p0 = target_match.get_target_param(self.p0)
    #     exprs = p0.expr_list
    #
    #     repl_matches = []
    #     splits = self.split_exprs(exprs)
    #     for exprs0, exprs1 in splits:
    #         repl_match_copy = copy.deepcopy(repl_match)
    #         p1 = repl_match_copy.get_target_param(self.p1)
    #         p2 = repl_match_copy.get_target_param(self.p2)
    #         p1.init_from_expr_list(exprs0)
    #         p2.init_from_expr_list(exprs1)
    #         repl_matches.append(repl_match_copy)
    #
    #     return repl_matches
    #
    # @classmethod
    # def split_exprs(cls, exprs: list[str]) -> list[tuple[list[str], list[str]]]:
    #     splits = []
    #     for i in range(1, len(exprs)):
    #         groups = (exprs[:i], exprs[i:])
    #         splits.append(groups)
    #         # let FilterSwap rule handle the reverse case
    #         splits.append(groups[::-1])
    #     return splits
