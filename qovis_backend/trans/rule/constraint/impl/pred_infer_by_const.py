from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class PredInferByConst(TransConstraint):
    def __init__(self, p0: Predicate, p1: Predicate):
        super().__init__()
        self.p0 = p0
        self.p1 = p1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        p0 = target_match.get_target_param(self.p0)
        p1 = repl_match.get_target_param(self.p1)

        new_expr_set = set()
        new_expr_list = []
        for expr, reqs in zip(p0.expr_list, p0.reqs_list):
            if self.has_const(expr) and len(reqs) == 1:
                new_expr = f'isnotnull({reqs[0]})'
                if new_expr not in new_expr_set:
                    new_expr_set.add(new_expr)
                    new_expr_list.append(new_expr)

        p1.init_from_expr_list(new_expr_list + p0.expr_list)

        return [repl_match]

    def has_const(self, expr: str) -> bool:
        for sym in ['=', '>', '<', '>=', '<=']:
            if sym not in expr:
                continue
            # split by sym and check if any of the two parts is a number or a string
            parts = expr.split(sym)
            if len(parts) != 2:
                continue
            for part in parts:
                part = part.strip()
                if part.isdigit() or part.startswith('\'') or part.startswith('\"'):
                    return True
        return False

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        p0 = target_match.get_target_param(self.p0)
        p1 = repl_match.get_target_param(self.p1)
        node0 = p0.owner
        node1 = p1.owner
        name0 = p0.owner.get_param_name(p0)
        name1 = p1.owner.get_param_name(p1)

        links = []
        for idx1, expr1 in enumerate(p1.expr_list):
            if expr1.startswith('isnotnull('):
                continue
            idx0 = p0.expr_list.index(expr1)
            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))

        return links
