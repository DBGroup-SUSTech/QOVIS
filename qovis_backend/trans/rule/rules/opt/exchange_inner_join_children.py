from trans.plan.operator.impl.inner_join import InnerJoin
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.pred_size_le import PredSizeLe
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule


join0 = InnerJoin()
p_src = join0

join1 = InnerJoin()
p_dst = join1

ExchangeInnerJoinChildren = Rule(
    "ExchangeInnerJoinChildren",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        PredSizeLe(join0.pred, 0),
    ],
    trans_constraints=[
        # join1
        PredEq(join0.pred, join1.pred),
        # relation
        RelEq(join0.left_rel, join1.right_rel),
        RelEq(join0.right_rel, join1.left_rel),
    ]
)

