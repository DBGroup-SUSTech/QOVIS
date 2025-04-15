from trans.plan.operator.join_like import JoinLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class LeftAntiJoin(JoinLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        if '(' not in self.str_:
            pred_str = ""
        else:
            # Example: "Join LeftAnti, (lo_orderdate#23 = d_datekey#152)"
            pred_str = self.str_[self.str_.find("("): self.str_.rfind(")") + 1]
        self.pred.init_from_str(pred_str)

        self.complete_param_and_check()

    def compute_output_rel(self) -> Relation:
        rel = Relation()
        # left semi join only outputs left relation
        rel.set_attrs_from_list([a.copy() for a in self.left_rel.attrs])\
            .set_is_empty(self.left_rel.is_empty)
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        from_left = self.left_rel.includes_attr(attr)
        if from_left:
            return self.children[0].backtrace_attr(attr) or attr
        else:
            raise Exception("Attribute %s not found in the left side of join condition" % attr)

