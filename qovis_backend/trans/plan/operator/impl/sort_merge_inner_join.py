from trans.plan.operator.join_like import JoinLike
from trans.plan.param.attribute import Attribute
from trans.plan.param.relation import Relation


class SortMergeInnerJoin(JoinLike):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def is_concrete(cls) -> bool:
        return True

    def init(self):
        # Example: "SortMergeJoin [lo_orderdate#23], [d_datekey#152], Inner"
        left = self.str_[self.str_.find("[") + 1: self.str_.find("], [")]
        right = self.str_[self.str_.find("], [") + 4: self.str_.rfind("]")]
        self.pred.init_from_str(left + " = " + right)

        self.complete_param_and_check()

    def compute_output_rel(self) -> Relation:
        rel = Relation()
        rel.set_attrs_from_list([a.copy() for a in (self.left_rel.attrs.items + self.right_rel.attrs.items)])\
            .set_is_empty(self.left_rel.is_empty and self.right_rel.is_empty)
        return rel

    def backtrace_attr(self, attr: Attribute) -> Attribute:
        from_left = self.left_rel.includes_attr(attr)
        from_right = self.right_rel.includes_attr(attr)
        if from_left and from_right:
            raise Exception("Attribute %s appears on both sides of join condition" % attr)
        elif from_left:
            return self.children[0].backtrace_attr(attr)
        elif from_right:
            return self.children[1].backtrace_attr(attr)
        else:
            raise Exception("Attribute %s not found in either side of join condition" % attr)

