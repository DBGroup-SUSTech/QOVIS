from trans.plan.param.attributes import Attributes
from trans.plan.plan_match import PlanMatch
from trans.plan.plan_node import PlanNode
from trans.rule.constraint.src_constraint import ValidConstraint


class PSubAttrs(ValidConstraint):
    def __init__(self, a0: Attributes, a1: Attributes):
        super().__init__()
        self.a0 = a0
        self.a1 = a1

    def check(self, match: PlanMatch) -> bool:
        a0: Attributes = match.get_target_attrs(self.a0)
        node0: PlanNode = a0.get_owner_op()
        origin0 = Attributes()
        origin0.init([node0.backtrace_attr(a) for a in a0])

        a1: Attributes = match.get_target_attrs(self.a1)
        node1: PlanNode = a1.get_owner_op()
        origin1 = Attributes()
        origin1.init([node1.backtrace_attr(a) for a in a1])

        return len(origin0) < len(origin1) and origin0.is_subset_of(origin1)
