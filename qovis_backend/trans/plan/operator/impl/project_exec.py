from trans.plan.operator.proj_like import ProjLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class ProjectExec(ProjLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # parse '[id#2, _extract_n#60L AS _extract_n#59L]' to ['id#2', '_extract_n#60L AS _extract_n#59L']
        exprs_str = self.str_[self.str_.find("[") + 1: self.str_.find("]")]
        self.exprs.init_from_str(exprs_str)
        self.complete_param_and_check()

    def compute_output_rel(self) -> Relation:
        rel = Relation()
        rel.set_attrs_from(self.exprs.attrs)\
            .set_is_empty(self.rel.is_empty)
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        # first, try to find the src expression in exprs
        src_expr = self.exprs.find_produced_expr(attr)

        if src_expr is not None:
            # it is created by this operator
            if src_expr.is_attr():
                origin_attr = src_expr.attr  # also attr[0]
            elif src_expr.is_attr_rename():
                origin_attr = src_expr.attrs[0]
            else:
                # function and other expressions will not be backtraced
                return attr
        else:
            # then, try to find it in renamed attrs
            usages = self.exprs.find_usage_expr(attr)
            if len(usages) == 1 and usages[0].is_attr_rename():
                origin_attr = usages[0].attrs[0]
            else:
                return attr     # not found, stop backtrace

        return self.children[0].backtrace_attr(origin_attr)
