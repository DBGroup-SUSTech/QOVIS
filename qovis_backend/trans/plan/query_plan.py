import re
from functools import cached_property
from typing import Dict, Optional, List, Callable

from trans.plan.operator.input_like import InputLike
from trans.plan.operator.join_like import JoinLike
from trans.plan.param.base_param import BaseParam
from trans.plan.plan_node import PlanNode


class QueryPlan:
    def __init__(self, pid: int):
        self.pid = pid
        self.root: Optional[PlanNode] = None
        self.node_dict: Dict[int, PlanNode] = {}
        self.labels: List[str] = []
        self.resolved = False

    def init(self):
        def init_node(node: PlanNode):
            for child in node.children:
                init_node(child)
            node.init()
        init_node(self.root)
        self.resolved = True

    def complete_param(self):
        def _check_req(node: PlanNode):
            for child in node.children:
                _check_req(child)
            if not node.check_req():
                raise RuntimeError(f"An incomplete node is found: {node}")

        _check_req(self.root)

        def _complete_param(node: PlanNode):
            for child in node.children:
                _complete_param(child)
            node.complete_param_and_check()

        _complete_param(self.root)

    def shallow_copy_from(self, plan: 'QueryPlan'):
        self.pid = plan.pid
        self.root = plan.root
        self.node_dict = plan.node_dict
        self.labels = plan.labels

    def copy(self):
        """
        Node attributes and labels are shallow copied.
        """
        plan = QueryPlan(self.pid)
        plan.labels = self.labels.copy()

        # node dict
        for v in self.node_dict.values():
            plan.node_dict[v.vid] = v.copy()

        # build tree structure
        for v in self.node_dict.values():
            node = plan.node_dict[v.vid]
            node.children = [plan.node_dict[c.vid] for c in v.children]

        # root
        plan.root = plan.node_dict[self.root.vid]

        return plan

    def nodes(self):
        return list(self.node_dict.values())

    def __repr__(self):
        return f"Plan#{self.pid}"

    def equals(self, other: 'QueryPlan'):
        if not isinstance(other, QueryPlan):
            return False
        if len(self.node_dict) != len(other.node_dict):
            return False

        def is_same(node0: PlanNode, node1: PlanNode) -> bool:
            if not node0.fast_equals(node1):
                return False
            if len(node0.children) != len(node1.children):
                return False
            for u, v in zip(node0.children, node1.children):
                if not is_same(u, v):
                    return False
            return True

        return is_same(self.root, other.root)

    def semantically_equals(self, other: 'QueryPlan'):
        if not isinstance(other, QueryPlan):
            return False
        if len(self.node_dict) != len(other.node_dict):
            return False

        def is_semantically_same(node0: PlanNode, node1: PlanNode) -> bool:
            if not node0.semantically_equals(node1):
                return False
            if len(node0.children) != len(node1.children):
                return False
            for u, v in zip(node0.children, node1.children):
                if not is_semantically_same(u, v):
                    return False
            return True

        return is_semantically_same(self.root, other.root)

    def find_node(self, f: Callable[['PlanNode'], bool]) -> Optional['PlanNode']:
        for v in self.node_dict.values():
            if f(v):
                return v
        return None

    def find_node_preorder(self, f: Callable[['PlanNode'], bool]) -> Optional['PlanNode']:
        return self.root.find(f)

    def is_valid(self) -> bool:
        def _is_valid(node: PlanNode) -> bool:
            # check children number
            # disabled because of the EXISTS
            # if any(c is None for c in node.children) or len(node.children) != node.n_child:
            #     return False
            # check children
            for child in node.children:
                if not _is_valid(child):
                    return False
            # check node
            # all params is initialized
            for params in node.params.values():
                for param in params:
                    if not param.is_inited():
                        print(node, param)
                        return False
            return True
        return _is_valid(self.root)

    def dump(self) -> Dict:
        nodes = []
        for v in self.node_dict.values():
            nodes.append(v.dump())
        return {
            'pid': self.pid,
            'root': self.root.vid,
            'nodes': nodes,
            'labels': self.labels,
            'resolved': self.resolved,
        }

    @staticmethod
    def load(dct: Dict):
        raise NotImplementedError()

    def to_tree_repr(self):
        return self.root.to_tree_repr()
        # return self.root.to_tree_str(lambda v: repr(v))

    def to_hash_str(self) -> str:
        def _to_hash_str(node: PlanNode) -> str:
            param_str_list = []
            for kind, params in node.params.items():
                s = ','.join(p.to_hash_str() for p in params)
                param_str_list.append(f'{kind.name}={s}')
            return f"{node.name}" \
                   f"<{','.join(param_str_list)}>" \
                   f"({','.join([_to_hash_str(c) for c in node.children])})"
        result = _to_hash_str(self.root)
        # result = re.sub(r'#\d+', '', result)
        return result

    @cached_property
    def struct_list(self) -> List[str]:
        res = []
        for node in self.root.collect_all():
            if issubclass(node.__class__, InputLike):
                rels = node.params[BaseParam.Kind.REL]
                assert len(rels) != 0
                res.append(rels[0].name)
            elif issubclass(node.__class__, JoinLike):
                res.append('')
        return res

    def has_same_struct(self, other: 'QueryPlan') -> bool:
        return self.struct_list == other.struct_list
