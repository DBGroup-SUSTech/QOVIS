from trans.plan.operator.impl.serialize_from_object import SerializeFromObject
from trans.plan.operator.impl.subquery_alias import SubqueryAlias
from trans.plan.operator.impl.view import View
from trans.rule.constraint.impl.simple_param_eq import SimpleParamEq
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

subquery_alias = SubqueryAlias()
view = View()
sfo0 = SerializeFromObject()
p_src = subquery_alias\
    .add_child(view
               .add_child(sfo0))

sfo1 = SerializeFromObject()
p_dst = sfo1

RemoveAlias = Rule(
    "RemoveAlias",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        SimpleParamEq(sfo0.serializer, sfo1.serializer),
        # relation
        RelEq(sfo0.rel, sfo1.rel),
    ]
)

