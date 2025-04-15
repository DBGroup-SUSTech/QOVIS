from trans.plan.param.attributes import Attributes
from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class PredInferByAttrs(TransConstraint):
    def __init__(self, a0: Attributes, p1: Predicate):
        super().__init__()
        self.a0 = a0
        self.p1 = p1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        a0 = target_match.get_target_attrs(self.a0)
        p1 = repl_match.get_target_param(self.p1)

        new_expr_list = []
        for a in a0.items:
            new_expr = f'isnotnull({a.str})'
            new_expr_list.append(new_expr)

        p1.init_from_expr_list(new_expr_list)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        a0 = target_match.get_target_attrs(self.a0)
        p1 = repl_match.get_target_param(self.p1)
        node0 = target_match.get_target_node_by_attrs(self.a0)
        node1 = p1.owner
        name0 = node0.get_param_name(a0)
        name1 = p1.owner.get_param_name(p1)

        links = []
        for idx1, reqs in enumerate(p1.reqs_list):
            assert len(reqs) == 1       # isnotnull(xx)
            idx0 = a0.index(reqs[0])
            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))

        return links
