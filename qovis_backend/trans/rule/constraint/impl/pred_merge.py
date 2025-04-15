from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class PredMerge(TransConstraint):
    def __init__(self, p0: Predicate, p1: Predicate, p2: Predicate):
        super().__init__()
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        p0 = target_match.get_target_param(self.p0)
        p1 = target_match.get_target_param(self.p1)
        p2 = repl_match.get_target_param(self.p2)

        exprs = list(set(p0.expr_list + p1.expr_list))
        p2.init_from_expr_list(exprs)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        p0 = target_match.get_target_param(self.p0)
        p1 = target_match.get_target_param(self.p1)
        p2 = repl_match.get_target_param(self.p2)
        node0 = p0.owner
        node1 = p1.owner
        node2 = p2.owner
        name0 = node0.get_param_name(p0)
        name1 = node1.get_param_name(p1)
        name2 = node2.get_param_name(p2)
        # return [
        #     TransLink.mk_ch(node0, node2, name0, name2),
        #     TransLink.mk_ch(node1, node2, name1, name2)
        # ]
        links = []
        for idx0, expr in enumerate(p0.expr_list):
            idx2 = p2.expr_list.index(expr)
            links.append(TransLink.mk_ch(node0, node2, name0, name2, idx0, idx2))
        for idx1, expr in enumerate(p1.expr_list):
            idx2 = p2.expr_list.index(expr)
            links.append(TransLink.mk_ch(node1, node2, name1, name2, idx1, idx2))
        return links
