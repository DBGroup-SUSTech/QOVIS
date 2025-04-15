from trans.plan.operator.impl.filter import Filter
from trans.rule.constraint.impl.pred_merge import PredMerge
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

filter0 = Filter()
filter1 = Filter()
p_src = filter0\
    .add_child(filter1)

filter2 = Filter()
p_dst = filter2

CollapseFilter = Rule(
    "CollapseFilter",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # filter1 & filter2
        PredMerge(filter0.pred, filter1.pred, filter2.pred),
        # relation
        RelEq(filter1.rel, filter2.rel),
    ]
)

