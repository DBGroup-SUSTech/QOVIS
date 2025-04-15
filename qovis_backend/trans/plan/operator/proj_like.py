from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes
from trans.plan.param.expressions import Expressions
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class ProjLike(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.exprs: Expressions = self._add_exprs()
        self.rel: Relation = self._add_rel(required=False)

    @classmethod
    def is_concrete(cls) -> bool:
        return False

    def init(self):
        raise Exception("Not implemented")

    def complete_param_and_check(self):
        self.rel.init_from(self.children[0].compute_output_rel())

        # check
        for expr in self.exprs.expr_list:
            for attr in expr.attrs:
                if not self.rel.includes_attr(attr):
                    raise Exception("Attribute %s not found in relation %s" % (attr, self.rel))

    def compute_output_rel(self) -> Relation:
        raise Exception("Not implemented")

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        raise Exception("Not implemented")

    def dump_params(self) -> list[tuple[str, list]]:
        if not self.exprs:
            return PlanNode.dump_params(self)
        exprs: list[str] = list(map(lambda e: e.str, self.exprs.expr_list))
        # req_attrs: list[str] = list(map(lambda a: a.str, self.exprs.req_attrs.items))
        return [
            ("exprs", exprs),
            # ("reqAttrs", req_attrs)
        ]

    def get_param_name(self, param: Any) -> Optional[str]:
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
        for idx0, expr in enumerate(self.exprs.expr_list):
            eq_exprs = eq_node.exprs
            # assert isinstance(eq_exprs, Expressions)
            idx1 = eq_exprs.index_by_produced_attr(expr.attr)
            links.append(TransLink.mk_eq(self, eq_node, 'exprs', 'exprs', idx0, idx1))
        # for idx0, attr in enumerate(self.exprs.req_attrs.items):
        #     eq_req_attrs = eq_node.exprs.req_attrs
        #     assert isinstance(eq_req_attrs, Attributes)
        #     idx1 = eq_req_attrs.index(attr)
        #     links.append(TransLink.mk_eq(self, eq_node, 'reqAttrs', 'reqAttrs', idx0, idx1))
        return links

