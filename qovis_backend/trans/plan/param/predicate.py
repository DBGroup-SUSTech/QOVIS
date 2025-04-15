import re

from trans.common.re_pattern import AttrPattern
from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes
from trans.plan.param.base_param import BaseParam
from trans.plan.plan_utils import PlanUtils


class Predicate(BaseParam):
    def __init__(self):
        super().__init__(BaseParam.Kind.PRED)
        self.attrs = Attributes().set_owner_pred(self)
        self.expr_list: list[str] = []
        self.reqs_list: list[Attributes] = []

    def init_from_str(self, s: str):
        """
        Init from a string expression.
        Example: ((lo_suppkey#22 = s_suppkey#112) AND ((s_city#115 = UNITED KI1) OR (s_city#115 = UNITED KI5)))
        Result: ['lo_suppkey#22 = s_suppkey#112', '(s_city#115 = UNITED KI1) OR (s_city#115 = UNITED KI5)']
                [['lo_suppkey#22', 's_suppkey#112'], ['s_city#115']]
        """
        if s == "":
            return
        self.expr_list = sorted(PlanUtils.collect_and_expressions(s))
        self._init_attrs()
        self.inited = True

    def _init_attrs(self):
        attr_dict: dict[str, Attribute] = {}
        for expr in self.expr_list:
            raw_attrs = AttrPattern.findall(expr)
            refs = Attributes()
            for attr_str in raw_attrs:
                # ensure attr_str is not surrounded by quotes
                idx = expr.find(attr_str)
                if idx > 0 and expr[idx - 1] == '"':
                    continue
                # ensure attr_str is not like "outer(xxx)"
                if expr.find(f'outer({attr_str})') >= 0:
                    continue
                # ignore exists#xxx
                if attr_str.startswith('exists#'):
                    continue
                # add to self.attrs
                if attr_str not in attr_dict:
                    attr_obj = Attribute(attr_str)
                    attr_dict[attr_str] = attr_obj
                    self.attrs.add(attr_obj)
                # add to refs_list
                attr = attr_dict[attr_str]
                if attr not in refs:
                    refs.add(attr)
            self.reqs_list.append(refs)

    def item_cnt(self) -> int:
        return len(self.expr_list)

    def copy(self) -> 'Predicate':
        p = Predicate()
        p.init_from(self)
        return p

    def equals(self, other):
        if not isinstance(other, Predicate):
            return False
        if len(self.expr_list) != len(other.expr_list):
            return False
        for i in range(len(self.expr_list)):
            if self.expr_list[i] != other.expr_list[i]:
                return False
        return True

    def semantically_equals(self, other):
        return self.equals(other)   # todo

    def init_from(self, pred: 'Predicate'):
        self.attrs = pred.attrs.copy()\
            .set_owner_pred(self)
        self.expr_list = pred.expr_list.copy()
        self.reqs_list = pred.reqs_list.copy()
        self.inited = True

    def init_from_expr_list(self, expr_list: list[str]):
        self.expr_list = sorted(expr_list.copy())
        self._init_attrs()
        self.inited = True

    def __repr__(self):
        return f'Pred({self.expr_list})'

    def to_hash_str(self) -> str:
        expr_list = list(map(lambda s: re.sub(r'#\d+', '', s), self.expr_list))
        expr_list.sort()
        return f'{expr_list}'


def __test1():
    p = Predicate()
    p.init_from_str('((lo_suppkey#22 = s_suppkey#112) AND ((s_city#115 = UNITED KI1) OR (s_city#115 = UNITED KI5)))')
    print(p)
    print(p.attrs)
    assert len(p.attrs.items) == 3
    print(p.expr_list)
    assert len(p.expr_list) == 2
    print(p.reqs_list)
    assert len(p.reqs_list) == 2


def __test2():
    p = Predicate()
    p.init_from_str('(((lo_orderdate#23 = d_datekey#152) AND (d_year#156 = 1993)) AND (((lo_discount#29 >= 1) AND (lo_discount#29 <= 3)) AND (lo_quantity#26 < 25)))')
    print(p)
    print(p.attrs)
    assert len(p.attrs.items) == 5
    print(p.expr_list)
    assert len(p.expr_list) == 5
    print(p.reqs_list)
    assert len(p.reqs_list) == 5


def __test3():
    p = Predicate()
    p.init_from_str('((lo_orderdate#23 = d_datekey#152) AND (d_yearmonth#158 = Dec1997))')
    print(p)
    print(p.attrs)
    assert len(p.attrs.items) == 3
    print(p.expr_list)
    assert len(p.expr_list) == 2
    print(p.reqs_list)
    assert len(p.reqs_list) == 2


if __name__ == '__main__':
    __test1()
    __test2()
    __test3()
