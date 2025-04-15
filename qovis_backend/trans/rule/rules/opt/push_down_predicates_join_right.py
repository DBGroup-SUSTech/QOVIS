from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.join_like import JoinLike
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.constraint.impl.sub_attrs import SubAttrs
from trans.rule.rule import Rule

filter0 = Filter()
join0 = JoinLike()
p_src = filter0\
    .add_child(join0)

filter1 = Filter()
join1 = JoinLike().bind(join0)
p_dst = join1\
    .add_child(None)\
    .add_child(filter1)

PushDownPredicatesJoinRight = Rule(
    "PushDownPredicatesJoinRight",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        SubAttrs(filter0.pred.attrs, join0.right_rel.attrs),
    ],
    trans_constraints=[
        # join1
        PredEq(join0.pred, join1.pred),
        # filter1
        PredEq(filter0.pred, filter1.pred),
        # relation
        RelEq(join0.left_rel, join1.left_rel),
        RelEq(join0.right_rel, filter1.rel),
    ]
)

