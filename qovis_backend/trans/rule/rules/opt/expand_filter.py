from trans.plan.operator.impl.filter import Filter
from trans.rule.constraint.impl.pred_size_ge import PredSizeGe
from trans.rule.constraint.impl.pred_split import PredSplit
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

filter0 = Filter()
p_src = filter0

filter1 = Filter()
filter2 = Filter()
p_dst = filter1\
    .add_child(filter2)

ExpandFilter = Rule(
    "ExpandFilter",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        PredSizeGe(filter0.pred, 2),
    ],
    trans_constraints=[
        # filter1 & filter2
        PredSplit(filter0.pred, filter1.pred, filter2.pred),
        # relation
        RelEq(filter0.rel, filter2.rel),
    ]
)

