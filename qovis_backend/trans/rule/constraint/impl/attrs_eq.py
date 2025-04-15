from typing import Union, Optional

from trans.plan.param.attributes import Attributes, AttrsBuilder
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


# class AttrsEq(TransConstraint):
#     def __init__(self, a0_or_builder: Union[Attributes, AttrsBuilder], a1: Attributes):
#         super().__init__()
#         self.a0: Optional[Attributes] = None
#         self.a0_builder: Optional[AttrsBuilder] = None
#         if isinstance(a0_or_builder, Attributes):
#             self.a0 = a0_or_builder
#         elif isinstance(a0_or_builder, AttrsBuilder):
#             self.a0_builder = a0_or_builder
#         else:
#             raise ValueError(f"Invalid type: {type(a0_or_builder)}")
#         self.a1 = a1
#
#     def need_computation(self) -> bool:
#         return self.a0_builder is not None
#
#     def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
#         """
#         target_match.target is the target plan tree.
#         target_match.pattern is the src pattern of rule.
#         repl_match.target is the repl plan tree.
#         repl_match.pattern is the dst pattern of rule.
#         """
#         a1 = repl_match.get_target_param(self.a1)  # a1 is in some node in repl plan tree
#         if self.need_computation():
#             symbols = self.a0_builder.collect_symbols()
#             sym2attrs = {sym: target_match.get_target_attrs(sym) for sym in symbols}
#             a0 = self.a0_builder.compute(sym2attrs)
#         else:
#             a0 = target_match.get_target_attrs(self.a0)     # a0 is in some node in target plan tree
#         a1.init_from(a0)
#
#         return [repl_match]
#
#     def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
#         if not self.need_computation():
#             return [(self.a0.owner, self.a1.owner, 'attrs', 'attrs')]

class AttrsEq(TransConstraint):
    def __init__(self, a0: Attributes, a1: Attributes):
        super().__init__()
        self.a0 = a0
        self.a1 = a1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        """
        target_match.target is the target plan tree.
        target_match.pattern is the src pattern of rule.
        repl_match.target is the repl plan tree.
        repl_match.pattern is the dst pattern of rule.
        """
        a0 = target_match.get_target_attrs(self.a0)  # a0 is in some node in target plan tree
        a1 = repl_match.get_target_param(self.a1)    # a1 is in some node in repl plan tree
        a1.init_from(a0)
        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        node0 = target_match.get_target_node_by_param(self.a0)
        node1 = repl_match.get_target_node_by_param(self.a1)
        a0 = target_match.get_target_attrs(self.a0)
        a1 = repl_match.get_target_attrs(self.a1)
        name0 = node0.get_param_name(a0)
        name1 = node1.get_param_name(a1)
        links = []
        for idx0, attr in enumerate(a0.items):
            idx1 = a1.index(attr)
            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))
        return links
