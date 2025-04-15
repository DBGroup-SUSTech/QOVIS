from trans.plan.plan_match import PlanMatch
from trans.plan.plan_node import PlanNode
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


# deprecated
class OpEq(TransConstraint):
    """
    When two operators need to set the same data for computation, add this constraint to copy the data.
    In other case, no need to add this constraint.
    An equal link will be added between the two operators.
    """

    def __init__(self, node0: PlanNode, node1: PlanNode):
        super().__init__()
        self.node0 = node0
        self.node1 = node1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        """
        target_match.target is the target plan tree.
        target_match.pattern is the src pattern of rule.
        repl_match.target is the repl plan tree.
        repl_match.pattern is the dst pattern of rule.
        """
        node0 = target_match.get_target_node(self.node0)
        node1 = repl_match.get_target_node(self.node1)
        node1.assign_from(node0)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        node0 = target_match.get_target_node(self.node0)
        node1 = repl_match.get_target_node(self.node1)
        return [TransLink.mk_eq(node0, node1)]