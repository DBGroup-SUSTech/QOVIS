from trans.plan.operator.input_like import InputLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class LocalRelation(InputLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # LocalRelation [value#16]
        # -> Rel#??(value#16)
        attr_str_list = self.str_[self.str_.find('[') + 1: self.str_.find(']')].split(',')
        self.rel.set_attrs_from_list([Attribute(s.strip()) for s in attr_str_list])\
            .set_is_empty('<empty>' in self.str_)

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.rel.find_attr(attr) or attr
