from trans.plan.operator.join_like import JoinLike
from trans.plan.param.expressions import as_exprs
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule
from trans.plan.operator.impl.project import Project

proj0 = Project()
join0 = JoinLike()
p_src = proj0\
    .add_child(join0)

proj1 = Project()
join1 = JoinLike().bind(join0)
proj2 = Project()
p_dst = proj1\
    .add_child(join1
               .add_child(None)
               .add_child(proj2))

PruneColumnsJoinRight = Rule(
    "PruneColumnsJoinRight",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # proj1
        ExprsEq(proj0.exprs, proj1.exprs),
        # join1
        PredEq(join0.pred, join1.pred),
        # proj2
        ExprsEq(as_exprs(join0.right_rel.attrs.intersect(join0.pred.attrs.union(proj0.exprs.req_attrs))),
                proj2.exprs),
        # relation
        RelEq(join0.left_rel, join1.left_rel),
        RelEq(join0.right_rel, proj2.rel),
    ]
)

