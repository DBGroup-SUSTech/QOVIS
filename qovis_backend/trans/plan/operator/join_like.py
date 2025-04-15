import sys
from abc import ABC
from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes
from trans.plan.param.predicate import Predicate
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class JoinLike(PlanNode, ABC):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 2

        self.pred: Predicate = self._add_pred()
        self.left_attrs: Attributes = self._add_attrs(required=False)
        self.right_attrs: Attributes = self._add_attrs(required=False)
        self.left_rel: Relation = self._add_rel(required=False)
        self.right_rel: Relation = self._add_rel(required=False)
    
    @classmethod
    def is_concrete(cls) -> bool:
        return False

    def complete_param_and_check(self):
        self.left_rel.init_from(self.children[0].compute_output_rel())
        self.right_rel.init_from(self.children[1].compute_output_rel())

        left, right = [], []
        for attr in self.pred.attrs:
            from_left = self.left_rel.includes_attr(attr)
            from_right = self.right_rel.includes_attr(attr)
            if from_left and from_right:
                # raise Exception("Attribute %s appears on both sides of join condition" % attr)
                sys.stderr.write(f"Attribute {attr} appears on both sides of join condition. Append to both sides.\n")
                left.append(attr)
                right.append(attr)
            elif from_left:
                left.append(attr)
            elif from_right:
                right.append(attr)
            else:
                # raise Exception("Attribute %s not found in either side of join condition" % attr)
                sys.stderr.write(f"Attribute {attr} not found in either side of join condition. Ignored.\n")
        self.left_attrs.init(left)
        self.right_attrs.init(right)

    def compute_output_rel(self) -> Relation:
        raise Exception("Not implemented")

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        raise Exception("Not implemented")

    def dump_params(self) -> list[tuple[str, list]]:
        return [
            ("pred", self.pred.expr_list),
            # ("leftAttrs", list(map(lambda a: a.str, self.left_attrs.items))),
            # ("rightAttrs", list(map(lambda a: a.str, self.right_attrs.items))),
            # ("leftRelAttrs", list(map(lambda a: a.str, self.left_rel.attrs.items))),
            # ("rightRelAttrs", list(map(lambda a: a.str, self.right_rel.attrs.items))),
        ]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.pred:
            return "pred"
        # we link these attributes to pred
        if param is self.pred.attrs:
            return "pred"
        if param is self.left_rel.attrs or param is self.right_rel.attrs:
            return "pred"
        # if param is self.left_attrs or param is self.right_attrs:
        #     return "pred"
        # if param is self.left_rel.attrs:
        #     return "leftRelAttrs"
        # elif param is self.right_rel.attrs:
        #     return "rightRelAttrs"
        return None

    def build_eq_links(self, eq_node: PlanNode) -> list[TransLink]:
        if not self.semantically_equals(eq_node):
            raise RuntimeError(f"Cannot build link between {self} and {eq_node}")
        links = []
        for idx0, expr in enumerate(self.pred.expr_list):
            idx1 = eq_node.pred.expr_list.index(expr)
            links.append(TransLink.mk_eq(self, eq_node, 'pred', 'pred', idx0, idx1))
        # for idx0, attr in enumerate(self.left_attrs.items):
        #     idx1 = eq_node.left_attrs.index(attr)
        #     links.append(TransLink.mk_eq(self, eq_node, 'leftAttrs', 'leftAttrs', idx0, idx1))
        # for idx0, attr in enumerate(self.right_attrs.items):
        #     idx1 = eq_node.right_attrs.index(attr)
        #     links.append(TransLink.mk_eq(self, eq_node, 'rightAttrs', 'rightAttrs', idx0, idx1))
        return links
