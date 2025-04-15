from trans.rule.constraint.impl.exprs_eq import ExprsEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.constraint.impl.sub_attrs import SubAttrs
from trans.rule.rule import Rule
from trans.plan.operator.impl.project import Project

proj0 = Project()
proj1 = Project()
p_src = proj0\
    .add_child(proj1)

proj2 = Project()
p_dst = proj2

CollapseProject = Rule(
    "CollapseProject",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        # CanExprCollapse(proj1.exprs, proj0.exprs),
        SubAttrs(proj0.exprs.req_attrs, proj1.exprs.attrs),     # might throw error
    ],
    trans_constraints=[
        # proj2
        ExprsEq(proj1.exprs.collapse_to(proj0.exprs), proj2.exprs),
        # relation
        RelEq(proj1.rel, proj2.rel),
    ]
)

