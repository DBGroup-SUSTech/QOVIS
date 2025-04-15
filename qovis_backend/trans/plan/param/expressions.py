from typing import Optional, Union

from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes, AttrsBuilder
from trans.plan.param.builder import Builder
from trans.plan.param.expression import Expression
from trans.plan.param.base_param import BaseParam


class Expressions(BaseParam):
    def __init__(self):
        super().__init__(BaseParam.Kind.EXPRS)
        self.expr_list: list[Expression] = []
        self.attrs = Attributes().set_owner_exprs(self)         # output attrs
        self.req_attrs = Attributes().set_owner_exprs(self)     # input attrs

    def init_from_str(self, s: str) -> 'Expressions':
        """
        Init from a string expressions.
        Example: col1#1, col2#2 as col3#3, min(col4#4) as col5#5
        A special case: '*',
        """
        if s == "":
            return self
        raw_exprs = s.split(",")    # do not consider multi-param functions
        expr_list = [Expression(e.strip()) for e in raw_exprs]
        return self.init_from_expr_list(expr_list)

    def init_from_attrs(self, attrs: Attributes) -> 'Expressions':
        expr_list = [Expression(a.str) for a in attrs.items]
        return self.init_from_expr_list(expr_list)

    def init_from_expr_list(self, expr_list: list[Expression]) -> 'Expressions':
        self.expr_list = expr_list.copy()
        for expr in self.expr_list:
            self.attrs.add(expr.attr)
            self.req_attrs.union_in_place(expr.attrs)
        self.inited = True
        return self

    def init_from(self, exprs: 'Expressions'):
        self.attrs = exprs.attrs.copy()\
            .set_owner_exprs(self)
        self.req_attrs = exprs.req_attrs.copy()\
            .set_owner_exprs(self)
        self.expr_list = exprs.expr_list.copy()
        self.inited = True

    def item_cnt(self) -> int:
        return len(self.expr_list)

    def copy(self) -> 'Expressions':
        exprs = Expressions()
        exprs.init_from(self)
        return exprs

    def equals(self, other):
        if not isinstance(other, Expressions):
            return False
        if len(self.expr_list) != len(other.expr_list):
            return False
        # for i in range(len(self.expr_list)):
        #     if not self.expr_list[i].equals(other.expr_list[i]):
        #         return False
        for expr in self.expr_list:
            if not other.find_produced_expr(expr.attr):
                return False
        return True

    def semantically_equals(self, other):
        # todo fix bug
        if not isinstance(other, Expressions):
            return False
        if len(self.expr_list) != len(other.expr_list):
            return False
        for expr in self.expr_list:
            if not self._has_same_expr(other, expr):        # do not consider star expand
                return False
        return True

    def _has_same_expr(self, other: 'Expressions', expr: Expression) -> bool:
        if other.find_produced_expr(expr.attr):
            return True
        for e in other.expr_list:
            if e.attrs.is_subset_of(expr.attrs) and expr.attrs.is_subset_of(e.attrs):
                return True

    def __len__(self):
        return len(self.expr_list)

    def __str__(self):
        return f'e{self.expr_list}'

    def __repr__(self):
        return str(self)

    def to_hash_str(self) -> str:
        expr_list = [e.to_hash_str() for e in self.expr_list]
        expr_list.sort()
        return f'{expr_list}'

    def find_produced_expr(self, attr: Attribute) -> Optional[Expression]:
        for expr in self.expr_list:
            if expr.attr.equals(attr):
                return expr
        return None

    def find_usage_expr(self, attr: Attribute) -> list[Expression]:
        res = []
        for expr in self.expr_list:
            if expr.attrs.includes(attr):
                res.append(expr)
        return res

    def index_by_produced_attr(self, attr: Attribute) -> int:
        for i, e in enumerate(self.expr_list):
            if e.attr.equals(attr):
                return i
        return -1

    def collapse_to_immediately(self, other: 'Expressions') -> 'Expressions':
        expr_list = []
        for target in other.expr_list:
            req_attrs = target.attrs
            expr = target.copy()
            for req in req_attrs:
                source = self.find_produced_expr(req)
                if source is None:
                    raise Exception(f"Cannot find {req} in {self.expr_list}")
                expr = source.collapse_to(expr)
            expr_list.append(expr)
        exprs = Expressions()
        exprs.init_from_expr_list(expr_list)
        return exprs

    def collapse_to(self, other: Union['Exprssions', 'ExprsBuilder']) -> 'ExprsBuilder':
        return ExprsBuilder(Builder.Kind.COLLAPSE_TO, self, other)


class ExprsBuilder(Builder):
    def __init__(self, kind: Builder.Kind,
                 left: Union[Expressions, 'ExprsBuilder', Attributes, AttrsBuilder],
                 right: Union[Expressions, 'ExprsBuilder', None]):
        super().__init__(kind, left, right)

    def collapse_to(self, o: Union[Expressions, 'ExprsBuilder']) -> 'ExprsBuilder':
        return ExprsBuilder(ExprsBuilder.Kind.COLLAPSE_TO, self, o)

    def compute(self, sym2exprs_or_attrs: dict[Union[Expressions, Attributes],
                                               Union[Expressions, Attributes]]) -> Expressions:
        left = self.get_or_compute(self.left, sym2exprs_or_attrs)
        right = self.get_or_compute(self.right, sym2exprs_or_attrs)

        if self.kind == ExprsBuilder.Kind.COLLAPSE_TO:
            assert isinstance(left, Expressions)
            assert isinstance(right, Expressions)
            return left.collapse_to_immediately(right)
        elif self.kind == ExprsBuilder.Kind.ATTRS_AS_EXPRS:
            assert isinstance(left, Attributes)
            return as_exprs_immediately(left)
        else:
            raise Exception(f"Unknown AttrsExpression.Kind: {self.kind}")


def as_exprs_immediately(attrs: Attributes) -> Expressions:
    return Expressions().init_from_attrs(attrs)


def as_exprs(attrs: Union[Attributes, AttrsBuilder]) -> ExprsBuilder:
    return ExprsBuilder(ExprsBuilder.Kind.ATTRS_AS_EXPRS, attrs, None)


def __inner_test():
    pe0 = Expressions()
    pe1 = Expressions()

    builder = pe1.collapse_to(pe0)

    e0 = Expressions()
    e1 = Expressions()

    # results:        a#1, b#2 AS i#9, c#3 AS j#10, min(e#5) AS f#6, max(g#7) AS k#11
    e0.init_from_str("a#1, b#2 AS i#9, d#4 AS j#10, f#6,             h#8 AS k#11")
    e1.init_from_str("a#1, b#2,        c#3 AS d#4,  min(e#5) AS f#6, max(g#7) AS h#8")

    sym2exprs = {pe0: e0, pe1: e1}
    print(builder.compute(sym2exprs))


if __name__ == '__main__':
    __inner_test()
