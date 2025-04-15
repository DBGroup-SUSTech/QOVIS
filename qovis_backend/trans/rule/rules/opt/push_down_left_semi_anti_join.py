from trans.plan.operator.impl.left_anti_join import LeftAntiJoin
from trans.plan.operator.impl.project import Project
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule


join0 = LeftAntiJoin()
proj0 = Project()
p_src = join0\
    .add_child(proj0)\
    .add_child(None)

proj1 = Project()
join1 = LeftAntiJoin()
p_dst = proj1\
    .add_child(join1)

PushDownLeftSemiAntiJoinLeft = Rule(
    "PushDownLeftSemiAntiJoinLeft",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # join1
        PredEq(join0.pred, join1.pred),
        # project1
        ExprsEq(proj0.exprs, proj1.exprs),
        # relation
        RelEq(proj0.rel, join1.left_rel),
        RelEq(join0.right_rel, join1.right_rel),
    ]
)

