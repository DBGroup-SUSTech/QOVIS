from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class UnresolvedHint(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.strategy = self._add_str()
        self.side = self._add_str()
        self.rel = self._add_rel(required=False)
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # Example
        # 'UnresolvedHint BROADCAST, ['t]
        # -> BROADCAST and 't
        self.strategy.init(self.str_.split(' ')[1].split(',')[0])
        self.side.init(self.str_[self.str_.find('[') + 1: self.str_.find(']')])
        self.complete_param_and_check()

    def complete_param_and_check(self):
        self.rel.init_from(self.children[0].compute_output_rel())

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.children[0].backtrace_attr(attr)

    def dump_params(self) -> list[tuple[str, list]]:
        return [
            ("strategy", [self.strategy.value]),
            ("side", [self.side.value])
        ]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.strategy:
            return "strategy"
        elif param is self.side:
            return "side"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            raise RuntimeError(f"Cannot build link between {self} and {eq_node}")
        return [
            TransLink.mk_eq(self, eq_node, "strategy", "strategy"),
            TransLink.mk_eq(self, eq_node, "side", "side")
        ]
