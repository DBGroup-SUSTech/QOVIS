from typing import Any, Optional

from trans.plan.operator.input_like import InputLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class ExternalRddScanExec(InputLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # ExternalRDD#9341(addr=-407569402,attrs=[ExternalRDD [obj#17])]
        # -> obj#17[]
        name = self.str_[self.str_.rfind('[') + 1: self.str_.rfind(']')]
        is_empty = '<empty>' in self.str_
        self.rel.init(name, [], is_empty)

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.rel.find_attr(attr) or attr