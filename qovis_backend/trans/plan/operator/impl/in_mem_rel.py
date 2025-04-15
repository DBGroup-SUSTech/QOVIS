from typing import Any, Optional

from trans.plan.operator.input_like import InputLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class InMemoryRelation(InputLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # InMemoryRelation [id#2, nested#3], StorageLevel(disk, memory, deserialized, 1 replicas)
        # -> UnknownRel#0[id#2, nested#3]
        attr_str_list = self.str_[self.str_.find('[') + 1: self.str_.find(']')]
        is_empty = '<empty>' in self.str_
        self.rel.init("UnknownRel", [Attribute(a) for a in attr_str_list.split(',')], is_empty)

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.rel.find_attr(attr) or attr

    # def dump_params(self) -> list[tuple[str, Any]]:
    #     return [("attrs", self.rel.get_attr_list())]
    #
    # def get_param_name(self, param: Any) -> Optional[str]:
    #     if param is self.rel:
    #         return "attrs"
    #     return None
