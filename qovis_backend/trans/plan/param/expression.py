import re
from enum import Enum

from trans.common.re_pattern import FullAttrPattern, RenamePattern, FuncPattern, OtherPattern, AttrPattern
from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes


class Expression:
    class Kind(Enum):
        UNKNOWN = 0
        ATTR = 1
        ATTR_RENAME = 2
        FUNCTION = 3
        STAR = 4
        OTHER = 5

    def __init__(self, str_: str = ""):
        self.str = str_.strip()
        self.attr: Attribute = None     # output attribute
        self.attrs = Attributes()       # required input attribute
        self.expr: str = ''
        self.kind: Expression.Kind = Expression.Kind.UNKNOWN

        self._init_from_str()

    def _init_from_str(self):
        s = self.str

        if FullAttrPattern.match(s):
            self.attr = Attribute(s)
            self.attrs.add(self.attr)
            self.expr = ''
            self.kind = Expression.Kind.ATTR

        elif RenamePattern.match(s):
            # rename attribute
            arr = s.split(" AS ")
            self.attr = Attribute(arr[1])
            req_attr = Attribute(arr[0])
            self.attrs.add(req_attr)
            self.expr = arr[0]
            self.kind = Expression.Kind.ATTR_RENAME

        elif FuncPattern.match(s):
            arr = s.split(" AS ")
            self.attr = Attribute(arr[1])
            raw_attrs = AttrPattern.findall(arr[0])
            for raw_attr in raw_attrs:
                req_attr = Attribute(raw_attr)
                self.attrs.add(req_attr)
            self.expr = arr[0]
            self.kind = Expression.Kind.FUNCTION

        elif OtherPattern.match(s):
            arr = s.split(" AS ")
            self.attr = Attribute(arr[1])
            raw_attrs = AttrPattern.findall(arr[0])
            for raw_attr in raw_attrs:
                req_attr = Attribute(raw_attr)
                self.attrs.add(req_attr)
            self.expr = arr[0]
            self.kind = Expression.Kind.OTHER

        elif s == '*':
            self.attr = Attribute('')
            self.expr = '*'
            self.kind = Expression.Kind.STAR

        else:
            raise Exception(f"Unknown expression {self.str}")

    def is_attr(self):
        return self.kind == Expression.Kind.ATTR

    def is_attr_rename(self):
        return self.kind == Expression.Kind.ATTR_RENAME

    def is_function(self):
        return self.kind == Expression.Kind.FUNCTION

    def equals(self, other):
        """ Compare directly without finding reference. """
        if not isinstance(other, Expression):
            return False
        return self.attr.equals(other.attr) # todo: check expr

    def copy(self) -> 'Expression':
        return Expression(self.str)

    def collapse_to(self, o: 'Expression') -> 'Expression':
        if self.kind == Expression.Kind.ATTR:
            return o.copy()
        elif self.kind == Expression.Kind.ATTR_RENAME:
            if o.kind == Expression.Kind.ATTR:
                # o    = b
                # self = a as b
                return self.copy()  # a as b
            elif o.kind == Expression.Kind.ATTR_RENAME:
                # o    = b as c
                # self = a as b
                return Expression(f"{self.expr} AS {o.attr}")   # a as c
            elif o.kind == Expression.Kind.FUNCTION:
                # o    = f(b) as c
                # self = a as b
                expr = o.expr.replace(f"{self.attr}", self.expr)
                return Expression(f"{expr} AS {o.attr}")  # f(a) as c
        elif self.kind == Expression.Kind.FUNCTION or self.kind == Expression.Kind.OTHER:
            if o.kind == Expression.Kind.ATTR:
                # o    = b
                # self = f(a) as b
                return self.copy()
            elif o.kind == Expression.Kind.ATTR_RENAME:
                # o    = b as c
                # self = f(a) as b
                return Expression(f"{self.expr} AS {o.attr}")   # f(a) as c

        raise Exception(f"Failed to collapse {self} to {o}")

    def can_collapse_to(self, o: 'Expression') -> bool:
        if self.kind == Expression.Kind.ATTR:
            return True
        elif self.kind == Expression.Kind.ATTR_RENAME:
            if o.kind == Expression.Kind.ATTR:
                return True
            elif o.kind == Expression.Kind.ATTR_RENAME:
                return True
            elif o.kind == Expression.Kind.FUNCTION:
                return True
        elif self.kind == Expression.Kind.FUNCTION or self.kind == Expression.Kind.OTHER:
            if o.kind == Expression.Kind.ATTR:
                return True
            elif o.kind == Expression.Kind.ATTR_RENAME:
                return True

        return False

    def __repr__(self):
        return f'{self.str}'

    def to_hash_str(self):
        s = re.sub(r'#\d+', "", self.str)
        return s
