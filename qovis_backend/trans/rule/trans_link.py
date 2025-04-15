from enum import Enum
from typing import Optional, Union

from trans.plan.plan_node import PlanNode


class TransLink:
    class LinkKind(Enum):
        EQ = 'eq'
        CH = 'ch'
        PEQ = 'peq'

    UNCHANGED_STEP = ''
    GUESS_STEP = '?'

    @staticmethod
    def mk_eq(node0: PlanNode, node1: PlanNode,
              param0: str, param1: str,
              param_idx0: int = 0, param_idx1: int = 0,
              rules: Optional[list[Union[str, 'Rule']]] = None) -> 'TransLink':
        return TransLink(node0, node1, TransLink.LinkKind.EQ, param0, param1, param_idx0, param_idx1, rules)

    @staticmethod
    def mk_ch(node0: PlanNode, node1: PlanNode,
              param0: str, param1: str,
              param_idx0: int = 0, param_idx1: int = 0,
              rules: Optional[list[Union[str, 'Rule']]] = None) -> 'TransLink':
        return TransLink(node0, node1, TransLink.LinkKind.CH, param0, param1, param_idx0, param_idx1, rules)

    @staticmethod
    def mk_peq(node0: PlanNode, node1: PlanNode,
               param0: str, param1: str,
               param_idx0: int = 0, param_idx1: int = 0,
               rules: Optional[list[Union[str, 'Rule']]] = None) -> 'TransLink':
        return TransLink(node0, node1, TransLink.LinkKind.PEQ, param0, param1, param_idx0, param_idx1, rules)

    def __init__(self, node0: PlanNode, node1: PlanNode, kind: LinkKind,
                 param0: str, param1: str,
                 param_idx0: int, param_idx1: int,
                 rules: Optional[list[Union[str, 'Rule']]] = None):
        self.node0 = node0
        self.node1 = node1
        self.kind = kind
        self.param0 = param0
        self.param1 = param1
        self.param_idx0 = param_idx0
        self.param_idx1 = param_idx1
        self.rules = rules or []

    def merge(self, other: 'TransLink') -> 'TransLink':
        """
        Merge two links into one.
              EQ  CH  PEQ
        EQ    EQ  CH  PEQ
        CH    CH  CH  PEQ
        PEQ  PEQ PEQ  PEQ
        """
        assert self.node1.vid == other.node0.vid
        # process PEQ
        if self.kind == self.LinkKind.PEQ or other.kind == self.LinkKind.PEQ:
            return TransLink.mk_peq(self.node0, other.node1,
                                    self.param0, other.param1,
                                    self.param_idx0, other.param_idx1,
                                    self.rules + other.rules)
        # process EQ and CH
        if self.kind == self.LinkKind.EQ and other.kind == self.LinkKind.EQ:
            return TransLink.mk_eq(self.node0, other.node1,
                                   self.param0, other.param1,
                                   self.param_idx0, other.param_idx1,
                                   self.rules + other.rules)
        # elif other.kind == self.LinkKind.EQ:
        #     return TransLink.mk_ch(self.node0, other.node1,
        #                            self.param0, self.param1,
        #                            self.param_idx0, self.param_idx1)
        # elif self.kind == self.LinkKind.EQ:
        #     return TransLink.mk_ch(self.node0, other.node1,
        #                            other.param0, other.param1,
        #                            other.param_idx0, other.param_idx1)
        else:
            return TransLink.mk_ch(self.node0, other.node1,
                                   self.param0, other.param1,
                                   self.param_idx0, other.param_idx1,
                                   self.rules + other.rules)

    def __eq__(self, other: 'TransLink'):
        return self.node0 is other.node0 and \
               self.node1 is other.node1 and \
               self.kind == other.kind and \
               self.param0 == other.param0 and \
               self.param1 == other.param1 and \
               self.param_idx0 == other.param_idx0 and \
               self.param_idx1 == other.param_idx1

    def __str__(self):
        def node_str(node: PlanNode):
            return f'{node.name}#{node.vid}'

        def param_str(node, param, param_idx):
            return f'{node_str(node)}.{param}[{param_idx}]'

        if self.kind == self.LinkKind.EQ:
            return f'EqLink({param_str(self.node0, self.param0, self.param_idx0)} == ' \
                   f'{param_str(self.node1, self.param1, self.param_idx1)})'
        elif self.kind == self.LinkKind.CH:
            return f'ChLink({param_str(self.node0, self.param0, self.param_idx0)} -> ' \
                   f'{param_str(self.node1, self.param1, self.param_idx1)})'
        elif self.kind == self.LinkKind.PEQ:
            return f'PEqLink({param_str(self.node0, self.param0, self.param_idx0)} == ' \
                   f'{param_str(self.node1, self.param1, self.param_idx1)})'
        else:
            raise Exception(f'Unknown link kind {self.kind}')

    def dump(self):
        return {
            'vid0': self.node0.vid,
            'vid1': self.node1.vid,
            'kind': self.kind.value,
            'p0': self.param0,
            'p1': self.param1,
            'idx0': self.param_idx0,
            'idx1': self.param_idx1,
            'rules': [r if isinstance(r, str) else r.name for r in self.rules],
        }
