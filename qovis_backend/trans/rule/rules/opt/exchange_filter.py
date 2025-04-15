from trans.plan.operator.impl.filter import Filter
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

filter0 = Filter()
filter1 = Filter()
p_src = filter0\
    .add_child(filter1)

filter2 = Filter()
filter3 = Filter()
p_dst = filter2\
    .add_child(filter3)

ExchangeFilter = Rule(
    "ExchangeFilter",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # filter2
        PredEq(filter1.pred, filter2.pred),
        # filter3
        PredEq(filter0.pred, filter3.pred),
        # relation
        RelEq(filter1.rel, filter3.rel),
    ]
)

