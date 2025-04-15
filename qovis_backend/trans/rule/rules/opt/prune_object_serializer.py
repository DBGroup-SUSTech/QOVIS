from trans.plan.operator.impl.serialize_from_object import SerializeFromObject
from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.p_sub_attrs import PSubAttrs
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.constraint.impl.sfo_prune import SfoPrune
from trans.rule.rule import Rule
from trans.plan.operator.impl.project import Project

proj0 = Project()
sfo0 = SerializeFromObject()
p_src = proj0\
    .add_child(sfo0)

proj1 = Project()
sfo1 = SerializeFromObject()
p_dst = proj1\
    .add_child(sfo1)

PruneObjectSerializer = Rule(
    "PruneObjectSerializer",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        # in fact, this constraint is not necessary
        PSubAttrs(proj0.exprs.req_attrs, proj0.rel.attrs),
    ],
    trans_constraints=[
        # proj1
        ExprsEq(proj0.exprs, proj1.exprs),
        # sfo1
        SfoPrune(proj0.exprs.req_attrs, sfo0, sfo1),
        # relation
        RelEq(sfo0.rel, sfo1.rel),
    ]
)

