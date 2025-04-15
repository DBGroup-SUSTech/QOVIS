from functools import cached_property
from typing import Any, Optional

from trans.common.re_pattern import AttrPattern
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class SerializeFromObject(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.serializer = self._add_str()
        self.rel: Relation = self._add_rel(required=False)
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        self.serializer.init(self.str_[self.str_.find('[') + 1: self.str_.rfind(']')])
        self.complete_param_and_check()

    def complete_param_and_check(self):
        # find attributes like lo_orderkey#18
        attr_str_list = AttrPattern.findall(self.serializer.value)
        self.rel.init_from(self.children[0].compute_output_rel())
        # rewrite rel.attrs
        self.rel.set_attrs_from_list([Attribute(a) for a in attr_str_list])\
            .set_is_empty(self.rel.is_empty)

    def compute_output_rel(self) -> Relation:
        return self.rel.copy()

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.rel.find_attr(attr) or attr

    @cached_property
    def raw_cols(self) -> list[str]:
        s0 = self.serializer.value
        # split the string. example:
        # knownnotnull(assertnotnull(input[0, LineOrder, true])).lo_custkey AS lo_custkey#20, knownnotnull(assertnotnull(input[0, LineOrder, true])).lo_suppkey AS lo_suppkey#22, knownnotnull(assertnotnull(input[0, LineOrder, true])).lo_orderdate AS lo_orderdate#23, knownnotnull(assertnotnull(input[0, LineOrder, true])).lo_revenue AS lo_revenue#30
        brackets = 0
        raw_cols = []
        start = 0
        for i, c in enumerate(s0):
            if c == '[' or c == '(':
                brackets += 1
            elif c == ']' or c == ')':
                brackets -= 1
            elif c == ',' and brackets == 0:
                col_expr = s0[start:i]
                raw_cols.append(col_expr.strip())
                start = i + 1
        if start < len(s0):
            col_expr = s0[start:]
            raw_cols.append(col_expr.strip())
        return raw_cols

    def dump_params(self) -> list[tuple[str, list]]:
        return [('serializer', [self.serializer.value])]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.rel:
            return "serializer"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            return []
        return [TransLink.mk_eq(self, eq_node, "serializer", "serializer")]


