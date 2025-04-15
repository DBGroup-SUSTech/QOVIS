from typing import Callable, Optional

from trans.plan.operator.custom_op import CustomOp
from trans.plan.param.attribute import Attribute
from trans.plan.param.base_param import BaseParam
from trans.plan.param.relation import Relation

RelComputeFunc = Callable[['CustomOp2'], Relation]


class CustomOp2(CustomOp):
    def __init__(self):
        super().__init__()
        self.n_child = 2

        self.left_rel: Relation = self._add_rel()
        self.right_rel: Relation = self._add_rel()
        self.rel_compute_func: Optional[RelComputeFunc] = None
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def set_rel_compute_func(self, func: RelComputeFunc) -> 'CustomOp2':
        self.rel_compute_func = func
        return self

    def init(self):
        pass

    def complete_param_and_check(self):
        if not self.left_rel.is_inited():
            self.left_rel.init_from(self.children[0].compute_output_rel())
        if not self.right_rel.is_inited():
            self.right_rel.init_from(self.children[1].compute_output_rel())

    def compute_output_rel(self) -> Relation:
        if self.rel_compute_func is None:
            return Relation()
        return self.rel_compute_func(self)

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        from_left = self.left_rel.includes_attr(attr)
        from_right = self.right_rel.includes_attr(attr)
        if from_left and from_right:
            raise Exception("Attribute %s appears on both sides of join condition" % attr)
        elif from_left:
            return self.children[0].backtrace_attr(attr)
        elif from_right:
            return self.children[1].backtrace_attr(attr)
        else:
            raise Exception("Attribute %s not found in either side of join condition" % attr)
