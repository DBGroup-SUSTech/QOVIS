from typing import Any, Optional

from trans.plan.operator.proj_like import ProjLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class Aggregate(ProjLike):
    def __init__(self):
        super().__init__()
        self.keys = self._add_attrs()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # Example
        # 'Aggregate [d_year#156, c_nation#83], [d_year#156, c_nation#83, sum((lo_revenue#30 - lo_supplycost#31)) AS profit1#242L]'
        # or
        # 'Aggregate [sum((lo_extendedprice#27 * lo_discount#29)) AS revenue#242L]'
        # if # of '[' is 1, then keys is empty
        # if # of '[' is 2, then keys is not empty
        if self.str_.count("[") == 2:
            keys_str = self.str_[self.str_.find("[") + 1: self.str_.find("]")]
        else:
            keys_str = ""
        self.keys.init_from_str(keys_str)
        exprs_str = self.str_[self.str_.rfind("[") + 1: self.str_.rfind("]")]
        self.exprs.init_from_str(exprs_str)
        self.complete_param_and_check()

    def compute_output_rel(self) -> Relation:
        rel = Relation()
        rel.set_attrs_from(self.exprs.attrs)\
            .set_is_empty(self.rel.is_empty)
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        # first, try to find the src expression in exprs
        src_expr = self.exprs.find_produced_expr(attr)

        if src_expr is None:
            return attr     # not found, stop backtrace

        if src_expr.is_attr():
            origin_attr = src_expr.attr     # also attr[0]
        elif src_expr.is_attr_rename():
            origin_attr = src_expr.attrs[0]
        else:
            # function and other expressions will not be backtraced
            # this attribute is produced by this operator
            return attr

        return self.children[0].backtrace_attr(origin_attr)

    def dump_params(self) -> list[tuple[str, list]]:
        keys: list[str] = list(map(lambda a: a.str, self.keys.items))
        exprs: list[str] = list(map(lambda e: e.str, self.exprs.expr_list))
        # req_attrs: list[str] = list(map(lambda a: a.str, self.exprs.req_attrs.items))
        return [
            ("keys", keys),
            ("exprs", exprs),
            # ("reqAttrs", req_attrs)
        ]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.keys:
            return "keys"
        if param is self.exprs:
            return "exprs"
        # we bind req_attrs to exprs
        if param is self.exprs.req_attrs:
            return "exprs"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            raise RuntimeError(f"Cannot build link between {self} and {eq_node}")

        links = []
        for idx0, attr in enumerate(self.keys.items):
            eq_keys = eq_node.keys
            # assert isinstance(eq_keys, Attributes)
            idx1 = eq_keys.index(attr)
            links.append(TransLink.mk_eq(self, eq_node, 'keys', 'keys', idx0, idx1))
        for idx0, expr in enumerate(self.exprs.expr_list):
            eq_exprs = eq_node.exprs
            # assert isinstance(eq_exprs, Expressions)
            idx1 = eq_exprs.index_by_produced_attr(expr.attr)
            links.append(TransLink.mk_eq(self, eq_node, 'exprs', 'exprs', idx0, idx1))

        return links
