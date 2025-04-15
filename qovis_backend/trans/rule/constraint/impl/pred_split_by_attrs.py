from trans.plan.param.attributes import Attributes
from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class PredSplitByAttrs(TransConstraint):
    def __init__(self, p0: Predicate, p1: Predicate, p1_attrs: Attributes, p2: Predicate):
        super().__init__()
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p1_attrs = p1_attrs

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        p0 = target_match.get_target_param(self.p0)
        p1_attrs = target_match.get_target_attrs(self.p1_attrs)
        p1 = repl_match.get_target_param(self.p1)
        p2 = repl_match.get_target_param(self.p2)

        exprs0, exprs1 = [], []
        for expr, attrs in zip(p0.expr_list, p0.reqs_list):
            if attrs.is_subset_of(p1_attrs):
                # all attrs used in this expr are in p1_attrs
                exprs0.append(expr)
            else:
                exprs1.append(expr)

        p1.init_from_expr_list(exprs0)
        p2.init_from_expr_list(exprs1)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        p0 = target_match.get_target_param(self.p0)
        p1 = repl_match.get_target_param(self.p1)
        p2 = repl_match.get_target_param(self.p2)
        node0 = p0.owner
        node1 = p1.owner
        node2 = p2.owner
        name0 = node0.get_param_name(p0)
        name1 = node1.get_param_name(p1)
        name2 = node2.get_param_name(p2)
        # return [
        #     TransLink.mk_ch(node0, node1, name0, name1),
        #     TransLink.mk_ch(node0, node2, name0, name2)
        # ]

        links = []
        for idx1, expr in enumerate(p1.expr_list):
            idx0 = p0.expr_list.index(expr)
            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))
        for idx2, expr in enumerate(p2.expr_list):
            idx0 = p0.expr_list.index(expr)
            links.append(TransLink.mk_ch(node0, node2, name0, name2, idx0, idx2))
        return links

