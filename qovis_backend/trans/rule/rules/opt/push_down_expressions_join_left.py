from trans.plan.operator.impl.project import Project
from trans.plan.operator.join_like import JoinLike
from trans.rule.constraint.impl.exprs_pushdown import ExprsPushdown
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

proj0 = Project()
join0 = JoinLike()
proj1 = Project()
p_src = proj0\
    .add_child(join0
               .add_child(proj1)
               .add_child(None))

proj2 = Project()
join1 = JoinLike().bind(join0)
proj3 = Project()
p_dst = proj2\
    .add_child(join1
               .add_child(proj3)
               .add_child(None))

PushDownExpressionsJoinLeft = Rule(
    "PushDownExpressionsJoinLeft",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # proj2 & proj3
        ExprsPushdown(proj0.exprs, proj1.exprs, proj2.exprs, proj3.exprs),
        # join1
        PredEq(join0.pred, join1.pred),
        # relation
        RelEq(proj1.rel, proj3.rel),
        RelEq(join0.right_rel, join1.right_rel),
    ]
)

