from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.predicate import Predicate
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class FilterExec(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.pred: Predicate = self._add_pred()
        # self.pred.attrs
        self.rel: Relation = self._add_rel(required=False)
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # parse Filter (A = B)
        pred_str = self.str_.split('Filter ')[1]
        self.pred.init_from_str(pred_str)

        self.complete_param_and_check()

    def complete_param_and_check(self):
        self.rel.init_from(self.children[0].compute_output_rel())

        for attr in self.pred.attrs:
            if self.rel.find_attr(attr) is None:
                raise RuntimeError(f"Cannot find attribute {attr} in relation {self.rel}")

    def compute_output_rel(self) -> Relation:
        return self.rel.copy_with_new_id()      # because it changes the tuple set

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.children[0].backtrace_attr(attr)

    def dump_params(self) -> list[tuple[str, list]]:
        return [("pred", self.pred.expr_list)]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.pred:
            return "pred"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            raise RuntimeError(f"Cannot build link between {self} and {eq_node}")
        links = []
        for idx0, expr in enumerate(self.pred.expr_list):
            idx1 = eq_node.pred.expr_list.index(expr)
            links.append(TransLink.mk_eq(self, eq_node, 'pred', 'pred', idx0, idx1))
        return links
