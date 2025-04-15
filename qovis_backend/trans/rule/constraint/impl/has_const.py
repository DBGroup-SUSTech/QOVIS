from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.src_constraint import ValidConstraint


class HasConst(ValidConstraint):
    def __init__(self, p0: Predicate):
        super().__init__()
        self.p0 = p0

    def check(self, match: PlanMatch) -> bool:
        p0 = match.get_target_param(self.p0)
        return any(self.has_const(expr) for expr in p0.expr_list)

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
