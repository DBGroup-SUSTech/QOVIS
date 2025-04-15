from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.src_constraint import ValidConstraint


class PredSizeLe(ValidConstraint):
    def __init__(self, p0: Predicate, num: int):
        super().__init__()
        self.p0 = p0
        self.num = num

    def check(self, match: PlanMatch) -> bool:
        p0: Predicate = match.get_target_param(self.p0)
        return len(p0.expr_list) <= self.num

