from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.constraint import Constraint
from trans.rule.trans_link import TransLink


class TransConstraint(Constraint):
    def __init__(self):
        super().__init__()

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        raise NotImplementedError

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        raise NotImplementedError
