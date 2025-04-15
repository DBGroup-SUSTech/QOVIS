from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class InputLike(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 0

        self.rel: Relation = self._add_rel()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return False

    def init(self):
        raise Exception("Not implemented")

    def complete_param_and_check(self):
        pass
        # # no way to complete rel if missing
        # # it must be initialized in init()
        # if not self.rel.is_inited():
        #     raise RuntimeError(f"Cannot refine relation on a leaf node: {self.name}")

    def compute_output_rel(self) -> Relation:
        raise Exception("Not implemented")

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        raise Exception("Not implemented")

    def dump_params(self) -> list[tuple[str, list]]:
        # add first 3 attrs in rel. add ... if more than 3 attrs
        rel = f"{self.rel.name}" \
              f"{'<empty>' if self.rel.is_empty else ''}" \
              f"[{','.join(str(a) for a in self.rel.attrs[:3])}" \
              f"{',...' if len(self.rel.attrs) > 3 else ''}]"
        return [("rel", [rel])]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.rel:
            return "rel"
        if param is self.rel.attrs:
            return "rel"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            raise RuntimeError(f"Cannot build link between {self} and {eq_node}")
        return [TransLink.mk_eq(self, eq_node, 'rel', 'rel')]

