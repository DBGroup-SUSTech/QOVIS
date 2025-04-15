from typing import Any, Optional

from trans.plan.operator.custom_op import CustomOp
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class CustomOp1(CustomOp):
    def __init__(self):
        super().__init__()
        self.n_child = 1

        self.rel: Relation = self._add_rel()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        self.rel.init_from(self.children[0].compute_output_rel())

    def complete_param_and_check(self):
        if not self.rel.is_inited():
            self.rel.init_from(self.children[0].compute_output_rel())

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.children[0].backtrace_attr(attr)
