from typing import Optional

from trans.plan.operator.input_like import InputLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class ExternalRdd(InputLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # ExternalRDD [obj#17]
        # -> obj#17[]
        name = self.str_[self.str_.find('[') + 1: self.str_.find(']')]
        is_empty = '<empty>' in self.str_
        self.rel.init(name, [], is_empty)

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.rel.find_attr(attr) or attr
