from typing import Any, Optional

from trans.plan.operator.custom_op1 import CustomOp1
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class ReturnAnswer(CustomOp1):
    def __init__(self):
        super().__init__()
        self.set_name('ReturnAnswer')
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def dump_params(self) -> list[tuple[str, list]]:
        return []

    def get_param_name(self, param: Any) -> Optional[str]:
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        return []
