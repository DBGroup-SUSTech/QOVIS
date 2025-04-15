from trans.plan.param.base_param import BaseParam
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class SimpleParamEq(TransConstraint):
    def __init__(self, param0: BaseParam, param1: BaseParam):
        super().__init__()
        self.param0 = param0
        self.param1 = param1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        param0 = target_match.get_target_param(self.param0)
        param1 = repl_match.get_target_param(self.param1)
        param1.init_from(param0)
        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        node0 = target_match.get_target_node_by_param(self.param0)
        node1 = repl_match.get_target_node_by_param(self.param1)
        param0 = target_match.get_target_param(self.param0)
        param1 = repl_match.get_target_param(self.param1)
        name0 = node0.get_param_name(param0)
        name1 = node1.get_param_name(param1)
        return [TransLink.mk_eq(node0, node1, name0, name1)]
