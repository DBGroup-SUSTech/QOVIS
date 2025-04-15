from typing import TypeVar

from trans.plan.param.attributes import Attributes
from trans.plan.param.base_param import BaseParam
from trans.plan.plan_node import PlanNode


T = TypeVar('T', bound=BaseParam)


class PlanMatch:
    def __init__(self, target: PlanNode, pattern: PlanNode, target_root: PlanNode):
        self.target = target
        self.target_root = target_root      # the start of the match
        self.pattern = pattern
        # vid to node
        self.target_to_pattern: dict[int, PlanNode] = {}
        self.pattern_to_target: dict[int, PlanNode] = {}
        self._build_match(target_root, pattern)

    def _build_match(self, target_node: PlanNode, pattern_node: PlanNode):
        self.target_to_pattern[target_node.vid] = pattern_node
        self.pattern_to_target[pattern_node.vid] = target_node
        if len(pattern_node.children) != len(target_node.children):
            return
        for target_child, pattern_child in zip(target_node.children, pattern_node.children):
            if pattern_child is None:
                continue
            self._build_match(target_child, pattern_child)

    def get_target_param(self, pattern_param: T) -> T:
        """ Get the target param corresponding to the pattern param. The param can only belong to operator. """
        owner = pattern_param.owner
        target_node = self.pattern_to_target[owner.vid]
        param_index = owner.params[pattern_param.kind].index(pattern_param)
        return target_node.params[pattern_param.kind][param_index]

    def get_target_node_by_param(self, pattern_param: T) -> PlanNode:
        """ Get the target node corresponding to the pattern param. The param can only belong to operator. """
        owner = pattern_param.owner
        target_node = self.pattern_to_target[owner.vid]
        return target_node

    def get_target_node(self, pattern_node: PlanNode) -> PlanNode:
        return self.pattern_to_target[pattern_node.vid]

    def get_target_attrs(self, attrs: Attributes) -> Attributes:
        if attrs.is_output():
            return self.get_target_node(attrs.owner).output
        elif attrs.belongs_to_rel():
            rel = attrs.owner_rel
            return self.get_target_param(rel).attrs
        elif attrs.belongs_to_pred():
            pred = attrs.owner_pred
            return self.get_target_param(pred).attrs
        elif attrs.belongs_to_exprs():
            exprs = attrs.owner_exprs
            target_exprs = self.get_target_param(exprs)
            if exprs.req_attrs == attrs:
                return target_exprs.req_attrs
            else:
                return target_exprs.attrs
        else:
            assert attrs.belongs_to_op()
            return self.get_target_param(attrs)

    def get_target_node_by_attrs(self, attrs: Attributes) -> PlanNode:
        """
        Get the target node corresponding to the pattern attrs param.
        The param can belong to operator or operator param.
        """
        if attrs.is_output():
            return self.get_target_node(attrs.owner)
        elif attrs.belongs_to_rel():
            rel = attrs.owner_rel
            return self.get_target_node_by_param(rel)
        elif attrs.belongs_to_pred():
            pred = attrs.owner_pred
            return self.get_target_node_by_param(pred)
        elif attrs.belongs_to_exprs():
            exprs = attrs.owner_exprs
            return self.get_target_node_by_param(exprs)
        else:
            assert attrs.belongs_to_op()
            return self.get_target_node_by_param(attrs)
