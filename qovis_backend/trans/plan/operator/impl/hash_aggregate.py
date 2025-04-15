from trans.plan.operator.proj_like import ProjLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.expression import Expression
from trans.plan.param.relation import Relation


class HashAggregate(ProjLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # Example
        # "HashAggregate(keys=[c_city#82, s_city#115, d_year#156], functions=[partial_sum(lo_revenue#30)], output=[c_city#82, s_city#115, d_year#156, sum#249L])"
        keys = self.str_[self.str_.find("keys=[") + 6: self.str_.find("], functions=[")]
        keys = keys.split(", ")
        functions = self.str_[self.str_.find("functions=[") + 12: self.str_.find("], output=[")]
        assert len(functions) == 1
        func = functions[0]
        outputs = self.str_[self.str_.find("output=[") + 8: self.str_.find("])")]

        exprs = []
        for key in keys:
            exprs.append(Expression(key))
        exprs.append(Expression(f"{func} as {outputs[-1]}"))

        self.exprs.init_from_expr_list(exprs)
        self.complete_param_and_check()

    def compute_output_rel(self) -> Relation:
        rel = Relation()
        rel.set_attrs_from(self.exprs.attrs)\
            .set_is_empty(self.rel.is_empty)
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        # first, try to find the src expression in exprs
        src_expr = self.exprs.find_produced_expr(attr)

        if src_expr is None:
            return attr     # not found, stop backtrace

        if src_expr.is_attr():
            origin_attr = src_expr.attr     # also attr[0]
        elif src_expr.is_attr_rename():
            origin_attr = src_expr.attrs[0]
        else:
            # function and other expressions will not be backtraced
            # this attribute is produced by this operator
            return attr

        return self.children[0].backtrace_attr(origin_attr)
