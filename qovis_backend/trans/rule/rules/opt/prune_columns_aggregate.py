from trans.plan.operator.impl.aggregate import Aggregate
from trans.plan.param.expressions import as_exprs
from trans.rule.constraint.impl.attrs_eq import AttrsEq
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule
from trans.plan.operator.impl.project import Project

aggr0 = Aggregate()
p_src = aggr0

aggr1 = Aggregate()
proj0 = Project()
p_dst = aggr1\
    .add_child(proj0)

PruneColumnsAggregate = Rule(
    "PruneColumnsAggregate",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # aggr1
        AttrsEq(aggr0.keys, aggr1.keys),
        ExprsEq(aggr0.exprs, aggr1.exprs),
        # proj0
        ExprsEq(as_exprs(aggr0.exprs.req_attrs), proj0.exprs),
        # relation
        RelEq(aggr1.rel, proj0.rel),
    ]
)
