from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.join_like import JoinLike
from trans.rule.constraint.impl.pred_merge import PredMerge
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

filter0 = Filter()
join0 = JoinLike()
p_src = filter0\
    .add_child(join0)

join1 = JoinLike().bind(join0)
p_dst = join1

CollapseFilterToJoin = Rule(
    "CollapseFilterToJoin",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # join1
        PredMerge(filter0.pred, join0.pred, join1.pred),
        # relation
        RelEq(join0.left_rel, join1.left_rel),
        RelEq(join0.right_rel, join1.right_rel),
    ]
)

