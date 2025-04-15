from enum import Enum
from typing import Optional, Union

from trans.plan.param.attribute import Attribute
from trans.plan.param.builder import Builder
from trans.plan.param.base_param import BaseParam


class Attributes(BaseParam):
    class Kind(Enum):
        UNKNOWN = 0
        OUTPUT_ATTRS = 1
        REL_ATTRS = 2
        PRED_ATTRS = 3
        EXPRS_ATTRS = 4
        OP_ATTRS = 5

    def __init__(self):
        super().__init__(BaseParam.Kind.ATTRS)
        self.items: list[Attribute] = []
        self.attr_kind: Attributes.Kind = Attributes.Kind.UNKNOWN
        self.owner_rel: Optional['Relation'] = None
        self.owner_pred: Optional['Predicate'] = None
        self.owner_exprs: Optional['Expression'] = None

    def init(self, items: list[Attribute]) -> 'Attributes':
        self.items = items
        self.inited = True
        return self

    def init_from_str(self, s: str) -> 'Attributes':
        self.items = [Attribute(e.strip()) for e in s.split(",")]
        self.inited = True
        return self

    def init_from(self, attrs: 'Attributes') -> 'Attributes':
        self.items = [attr.copy() for attr in attrs.items]
        self.inited = True
        return self

    def as_output(self, owner: 'PlanNode') -> 'Attributes':
        self.set_owner(owner)
        self.attr_kind = Attributes.Kind.OUTPUT_ATTRS
        return self

    def belongs_to_rel(self) -> bool:
        return self.attr_kind == Attributes.Kind.REL_ATTRS

    def belongs_to_pred(self) -> bool:
        return self.attr_kind == Attributes.Kind.PRED_ATTRS

    def belongs_to_exprs(self) -> bool:
        return self.attr_kind == Attributes.Kind.EXPRS_ATTRS

    def belongs_to_op(self) -> bool:
        return self.attr_kind == Attributes.Kind.OP_ATTRS

    def is_output(self) -> bool:
        return self.attr_kind == Attributes.Kind.OUTPUT_ATTRS

    def set_owner(self, owner: 'PlanNode') -> 'Attributes':
        super().set_owner(owner)
        self.attr_kind = Attributes.Kind.OP_ATTRS
        return self

    def set_owner_rel(self, rel: 'Relation') -> 'Attributes':
        self.owner_rel = rel
        self.attr_kind = Attributes.Kind.REL_ATTRS
        return self

    def set_owner_pred(self, pred: 'Predicate') -> 'Attributes':
        self.owner_pred = pred
        self.attr_kind = Attributes.Kind.PRED_ATTRS
        return self

    def set_owner_exprs(self, exprs: 'Expressions') -> 'Attributes':
        self.owner_exprs = exprs
        self.attr_kind = Attributes.Kind.EXPRS_ATTRS
        return self

    def add(self, attr: Attribute):
        if not self.includes(attr):
            self.items.append(attr)

    def includes(self, attr: Attribute):
        """ Check directly without finding reference. """
        return self.find(attr) is not None

    def __getitem__(self, x: int):
        return self.items[x]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return f"a{self.items}"

    def to_hash_str(self):
        return ','.join([a.to_hash_str() for a in self.items])

    def equals(self, other):
        """ Compare directly without finding reference. """
        if not isinstance(other, Attributes):
            return False
        if len(self.items) != len(other.items):
            return False
        set0 = set(a.to_unique_str() for a in self.items)
        set1 = set(a.to_unique_str() for a in other.items)
        return set0 == set1

    def semantically_equals(self, other):
        return self.equals(other)

    def is_subset_of(self, other: 'Attributes'):
        if len(self) > len(other):
            return False
        set0 = set(a.to_unique_str() for a in self.items)
        set1 = set(a.to_unique_str() for a in other.items)
        return set0.issubset(set1)

    def copy(self) -> 'Attributes':
        res = Attributes()
        res.init_from(self)
        return res

    def union_in_place(self, other: 'Attributes') -> 'Attributes':
        for b in other.items:
            if not self.includes(b):
                self.items.append(b)
        return self

    def union_immediately(self, other: 'Attributes') -> 'Attributes':
        res = Attributes()
        new_items = self.items.copy()
        for b in other.items:
            if not self.includes(b):
                new_items.append(b)
        res.init(new_items)
        # print(f"union_immediately: {self} \\/ {other} = {res}")
        return res

    def intersect_immediately(self, other: 'Attributes') -> 'Attributes':
        res = Attributes()
        new_items = []
        for a in self.items:
            b = other.find(a)
            if b is not None:
                new_items.append(b)
        res.init(new_items)
        # print(f"intersect_immediately: {self} /\\ {other} = {res}")
        return res

    def rename_immediately(self, exprs: 'Expressions') -> 'Attributes':
        items = []
        used: set['Expression'] = set()
        for a in self.items:
            bs = exprs.find_usage_expr(a)
            assert len(bs) == 1, f"Cannot rename {a} by {exprs}"
            b = bs[0]
            assert b.is_attr() or b.is_attr_rename(), f"Cannot rename {a} by {b}"
            used.add(b)
            items.append(b.attr)
        assert len(used) == len(exprs), f"Cannot rename {self} by {exprs} as not all attrs are included"
        res = Attributes()
        res.init(items)
        # print(f"rename_immediately: {self} as {exprs} = {res}")
        return res

    # def as_exprs_immediately(self) -> Expressions:
    #     return Expressions().init_from_attrs(self)

    def union(self, other: Union['Attributes', 'AttrsBuilder']) -> 'AttrsBuilder':
        return AttrsBuilder(Builder.Kind.ATTRS_UNION, self, other)

    def intersect(self, other: Union['Attributes', 'AttrsBuilder']) -> 'AttrsBuilder':
        return AttrsBuilder(Builder.Kind.ATTRS_INTERSECT, self, other)

    def rename(self, other: Union['Expressions', 'ExprsBuilder']) -> 'AttrsBuilder':
        return AttrsBuilder(Builder.Kind.ATTRS_RENAME, self, other)

    # def as_exprs(self) -> ExprsBuilder:
    #     return ExprsBuilder(ExprsBuilder.Kind.FROM_ATTRS, self, None)

    def find(self, attr: Attribute) -> Optional[Attribute]:
        for a in self.items:
            if a.equals(attr):
                return a
        return None

    def index(self, attr: Attribute) -> int:
        for i, a in enumerate(self.items):
            if a.equals(attr):
                return i
        return -1

    def get_owner_op(self) -> 'PlanNode':
        if self.attr_kind == Attributes.Kind.OP_ATTRS or self.attr_kind == Attributes.Kind.OUTPUT_ATTRS:
            return self.owner
        elif self.attr_kind == Attributes.Kind.PRED_ATTRS:
            return self.owner_pred.owner
        elif self.attr_kind == Attributes.Kind.REL_ATTRS:
            return self.owner_rel.owner
        elif self.attr_kind == Attributes.Kind.EXPRS_ATTRS:
            return self.owner_exprs.owner
        else:
            raise Exception(f"Unknown attr kind {self.attr_kind}")


class AttrsBuilder(Builder):
    def __init__(self, kind: Builder.Kind,
                 left: Union[Attributes, 'AttrsBuilder'],
                 right: Union[Attributes, 'AttrsBuilder', 'Expressions', 'ExprsBuilder']):
        super().__init__(kind, left, right)

    def union(self, o: Union[Attributes, 'AttrsBuilder']) -> 'AttrsBuilder':
        return AttrsBuilder(Builder.Kind.ATTRS_UNION, self, o)

    def intersect(self, o: Union[Attributes, 'AttrsBuilder']) -> 'AttrsBuilder':
        return AttrsBuilder(AttrsBuilder.Kind.ATTRS_INTERSECT, self, o)

    def rename(self, o: Union['Expressions', 'ExprsBuilder']) -> 'AttrsBuilder':
        return AttrsBuilder(AttrsBuilder.Kind.ATTRS_RENAME, self, o)

    # def as_exprs(self) -> ExprsBuilder:
    #     return ExprsBuilder(ExprsBuilder.Kind.FROM_ATTRS, self, None)

    def compute(self, sym2attrs: dict[BaseParam, BaseParam]) -> Attributes:
        left = self.get_or_compute(self.left, sym2attrs)
        right = self.get_or_compute(self.right, sym2attrs)

        if self.kind == Builder.Kind.ATTRS_UNION:
            assert isinstance(left, Attributes)
            assert isinstance(right, Attributes)
            return left.union_immediately(right)
        elif self.kind == Builder.Kind.ATTRS_INTERSECT:
            assert isinstance(left, Attributes)
            assert isinstance(right, Attributes)
            return left.intersect_immediately(right)
        elif self.kind == Builder.Kind.ATTRS_RENAME:
            assert isinstance(left, Attributes)
            # assert isinstance(right, Expressions)
            return left.rename_immediately(right)
        else:
            raise Exception(f"Unknown AttrsBuilder.Kind: {self.kind}")


def __test():
    pa0 = Attributes()
    pa1 = Attributes()
    pa2 = Attributes()

    expr = pa0.union(pa1).intersect(pa2)  # (pa0 \/ pa1) /\ pa2

    a0 = Attributes()
    a0.init_from_str("a#0, b#1")
    a2 = Attributes()
    a2.init_from_str("c#2")
    a3 = Attributes()
    a3.init_from_str("a#0, c#2, d#3")

    # ({a#0, b#1} \/ {c#2}) /\ {a#0, c#2, d#3} = {a#0, c#2}
    sym2attrs = {pa0: a0, pa1: a2, pa2: a3}
    print(expr.compute(sym2attrs))  # {a#0, c#2}


if __name__ == '__main__':
    __test()




