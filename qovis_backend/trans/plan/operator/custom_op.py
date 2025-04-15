from abc import ABC
from typing import Any, Optional

from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class CustomOp(PlanNode, ABC):
    def __init__(self):
        super().__init__()
        self.name = 'Unknown'
        self.n_child = 0

    @classmethod
    def is_concrete(cls) -> bool:
        return False

    def set_name(self, name: str) -> 'CustomOp':
        self.name = name
        return self

    def dump_params(self) -> list[tuple[str, list]]:
        param_str = self.str_.split(' ', 1)[-1]
        return [('param', [param_str])]

    def get_param_name(self, param: Any) -> Optional[str]:
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        return []
