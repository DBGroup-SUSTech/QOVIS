from trans.plan.operator.impl.inner_join import InnerJoin
from trans.plan.operator.impl.project import Project
from trans.plan.param.expressions import as_exprs
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule


join0 = InnerJoin()
p_src = join0

proj1 = Project()
join1 = InnerJoin()
p_dst = proj1\
    .add_child(join1)

EnsureAttrsOrder = Rule(
    "EnsureAttrsOrder",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # proj1
        ExprsEq(as_exprs(join0.output), proj1.exprs),
        # join1
        PredEq(join0.pred, join1.pred),
        # relation
        RelEq(join0.left_rel, join1.left_rel),
        RelEq(join0.right_rel, join1.right_rel),
    ]
)

