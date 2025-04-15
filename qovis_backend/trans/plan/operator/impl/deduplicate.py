from typing import Any, Optional

from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation
from trans.plan.plan_node import PlanNode
from trans.rule.trans_link import TransLink


class Deduplicate(PlanNode):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.n_child = 1

        self.keys = self._add_attrs()
        self.rel = self._add_rel(required=False)
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # Example
        # 'Deduplicate [attr#123]'
        keys_str = self.str_[self.str_.find("[") + 1: self.str_.find("]")]
        self.keys.init_from_str(keys_str)
        self.complete_param_and_check()

    def complete_param_and_check(self):
        self.rel.init_from(self.children[0].compute_output_rel())

        # check
        for attr in self.keys:
            if not self.rel.includes_attr(attr):
                raise Exception("Attribute %s not found in relation %s" % (attr, self.rel))

    def compute_output_rel(self) -> Relation:
        rel = self.rel.copy()
        # todo add unique
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        return self.children[0].backtrace_attr(attr)

    def dump_params(self) -> list[tuple[str, list]]:
        keys: list[str] = list(map(lambda a: a.str, self.keys.items))
        return [("keys", keys)]

    def get_param_name(self, param: Any) -> Optional[str]:
        if param is self.keys:
            return "keys"
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

        return links
