from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.constraint import Constraint


class ValidConstraint(Constraint):
    def __init__(self):
        super().__init__()

    def check(self, match: PlanMatch) -> bool:
        raise NotImplementedError

    # def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> None:
    #     raise NotImplementedError
