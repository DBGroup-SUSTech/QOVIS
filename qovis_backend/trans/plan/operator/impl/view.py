from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class View(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.rel: Relation = self._add_rel()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        self.complete_param_and_check()

    def complete_param_and_check(self):
        self.rel.init_from(self.children[0].compute_output_rel())

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.children[0].backtrace_attr(attr)

    def dump_params(self) -> list[tuple[str, list]]:
        # find alias in `XXX`
        alias = self.str_.split('`')[1]
        return [('alias', [alias])]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.rel:
            return "alias"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            return []
        return [TransLink.mk_eq(self, eq_node, "alias", "alias")]
