from trans.plan.operator.custom_op import CustomOp
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class CustomOp0(CustomOp):
    def __init__(self):
        super().__init__()
        self.n_child = 0

        self.rel: Relation = self._add_rel()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def set_rel(self, rel: Relation) -> 'CustomOp0':
        self.rel.init_from(rel)
        return self

    def init(self):
        pass

    def complete_param_and_check(self):
        # no way to fix rel if missing
        if not self.rel.is_inited():
            raise RuntimeError(f"Cannot refine relation on a leaf node: {self.name}")

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.rel.find_attr(attr) or attr
