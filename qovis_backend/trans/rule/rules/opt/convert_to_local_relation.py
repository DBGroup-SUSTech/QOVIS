from trans.plan.operator.impl.local_relation import LocalRelation
from trans.plan.param.relation import as_rel
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule
from trans.plan.operator.impl.project import Project

proj0 = Project()
lr0 = LocalRelation()
p_src = proj0\
    .add_child(lr0)

lr1 = LocalRelation()
p_dst = lr1

ConvertToLocalRelation = Rule(
    "ConvertToLocalRelation",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # relation
        RelEq(as_rel(lr0.rel.attrs.rename(proj0.exprs)), lr1.rel),
    ]
)
