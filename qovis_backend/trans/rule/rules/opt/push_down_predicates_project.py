from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.impl.project import Project
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

filter0 = Filter()
proj0 = Project()
p_src = filter0\
    .add_child(proj0)

proj1 = Project()
filter1 = Filter()
p_dst = proj1\
    .add_child(filter1)

PushDownPredicatesProject = Rule(
    "PushDownPredicatesProject",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # proj1
        ExprsEq(proj0.exprs, proj1.exprs),
        # filter1
        PredEq(filter0.pred, filter1.pred),
        # relation
        RelEq(proj0.rel, filter1.rel),
    ]
)

