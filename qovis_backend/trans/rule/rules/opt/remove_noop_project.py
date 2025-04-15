from trans.plan.operator.impl.project import Project
from trans.rule.constraint.impl.attrs_eq_check import AttrsEqCheck
from trans.rule.rule import Rule

proj0 = Project()
p_src = proj0

p_dst = None

RemoveNoopProject = Rule(
    "RemoveNoopProject",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        AttrsEqCheck(proj0.output, proj0.rel.attrs),
    ],
)

