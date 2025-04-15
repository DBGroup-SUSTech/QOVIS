from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.join_like import JoinLike
from trans.rule.constraint.impl.pred_size_ge import PredSizeGe
from trans.rule.constraint.impl.pred_split import PredSplit
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule


join0 = JoinLike()
p_src = join0

filter0 = Filter()
join1 = JoinLike().bind(join0)
p_dst = filter0\
    .add_child(join1)

ExpandFilterFromJoinTop = Rule(
    "ExpandFilterFromJoinTop",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        PredSizeGe(join0.pred, 1),
    ],
    trans_constraints=[
        # join1 type
        # OpTypeEq(join1, join0),
        # filter0 & join1
        PredSplit(join0.pred, filter0.pred, join1.pred),
        # relation
        RelEq(join0.left_rel, join1.left_rel),
        RelEq(join0.right_rel, join1.right_rel),
    ]
)

