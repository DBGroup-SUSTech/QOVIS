from typing import Any, Optional

from trans.plan.operator.input_like import InputLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class UnresolvedRelation(InputLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # 'UnresolvedRelation [ids], [], false
        # -> ids#0[]
        arr = self.str_.split(',')
        rel_name = arr[0][arr[0].find('[') + 1: arr[0].find(']')]
        attr_str_list = arr[1][self.str_.find('[') + 1: self.str_.find(']')].split(',')
        # filter out empty string
        attr_str_list = [a for a in attr_str_list if a]
        is_empty = '<empty>' in self.str_
        self.rel.init(rel_name, [Attribute(a) for a in attr_str_list], is_empty)

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
