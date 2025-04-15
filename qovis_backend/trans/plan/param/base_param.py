from enum import Enum


class BaseParam:

    class Kind(Enum):
        ATTRS = 'attrs'
        PRED = 'pred'
        EXPRS = 'exprs'
        REL = 'rel'
        STR = 'str'
        OTHER = 'other'

    def __init__(self, kind: Kind):
        self.kind = kind
        # use '' to avoid circular reference
        self.owner: 'PlanNode' = None
        self.inited: bool = False

    def set_owner(self, owner) -> 'BaseParam':
        self.owner: 'PlanNode' = owner
        return self

    def is_inited(self) -> bool:
        return self.inited

    def init_from(self, other: 'BaseParam') -> 'BaseParam':
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def equals(self, other):
        raise NotImplementedError

    def to_hash_str(self) -> str:
        raise NotImplementedError

    def semantically_equals(self, other):
        raise NotImplementedError

