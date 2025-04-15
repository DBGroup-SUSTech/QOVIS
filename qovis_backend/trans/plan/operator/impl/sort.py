from typing import Any, Optional

from trans.plan.const.sort_kind import SortOrder, NullOrder
from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class Sort(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.sorted_attrs: Attributes = self._add_attrs()
        self.sort_orders: list[SortOrder] = []
        self.null_orders: list[NullOrder] = []
        self.rel: Relation = self._add_rel(required=False)
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # Example:
        # Sort [d_year#156 ASC NULLS FIRST, revenue#242L DESC NULLS LAST], true
        attrs: list[Attribute] = []
        str_list = self.str_[self.str_.find("[") + 1: self.str_.find("]")].split(",")
        for s in str_list:
            arr = s.strip().split(" ", 2)
            assert len(arr) == 3
            attrs.append(Attribute(arr[0]))
            self.sort_orders.append(SortOrder.from_str(arr[1]))     # ASC or DESC
            self.null_orders.append(NullOrder.from_str(arr[2]))     # NULLS FIRST or NULLS LAST
        self.sorted_attrs.init(attrs)

        self.complete_param_and_check()

    def complete_param_and_check(self):
        self.rel.init_from(self.children[0].compute_output_rel())

    def compute_output_rel(self) -> Relation:
        rel = self.rel.copy()
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.children[0].backtrace_attr(attr)

    def dump_params(self) -> list[tuple[str, list]]:
        str_list = self.str_[self.str_.find("[") + 1: self.str_.find("]")].split(",")
        return [('sorted_attrs', str_list)]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.sorted_attrs:
            return "sorted_attrs"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            raise RuntimeError(f"Cannot build link between {self} and {eq_node}")
        links = []
        for idx0, attr in enumerate(self.sorted_attrs.items):
            idx1 = eq_node.sorted_attrs.index(attr)
            links.append(TransLink.mk_eq(self, eq_node, 'sorted_attrs', 'sorted_attrs', idx0, idx1))
        return links


