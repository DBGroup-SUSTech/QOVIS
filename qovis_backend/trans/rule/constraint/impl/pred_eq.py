from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class PredEq(TransConstraint):
    def __init__(self, p0: Predicate, p1: Predicate):
        super().__init__()
        self.p0 = p0
        self.p1 = p1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        p0 = target_match.get_target_param(self.p0)
        p1 = repl_match.get_target_param(self.p1)
        p1.init_from(p0)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        node0 = target_match.get_target_node_by_param(self.p0)
        node1 = repl_match.get_target_node_by_param(self.p1)
        # return [
        #     TransLink.mk_eq(node0, node1)       # now all rule using this constraint create equal link
        # ]
        p0 = target_match.get_target_param(self.p0)
        p1 = repl_match.get_target_param(self.p1)
        name0 = node0.get_param_name(p0)
        name1 = node1.get_param_name(p1)
        links = []
        for idx0, expr in enumerate(p0.expr_list):
            idx1 = p1.expr_list.index(expr)
            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))
        return links
