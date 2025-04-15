from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.impl.left_anti_join import LeftAntiJoin
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.pred_infer_by_attrs import PredInferByAttrs
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

la_join0 = LeftAntiJoin()
p_src = la_join0


la_join1 = LeftAntiJoin()
filter0 = Filter()
p_dst = la_join1\
    .add_child(None)\
    .add_child(filter0)

InferFilterFromLeftAntiJoin = Rule(
    "InferFilterFromLeftAntiJoin",
    Rule.OPT, p_src, p_dst,
    trans_constraints=[
        # la_join1
        PredEq(la_join0.pred, la_join1.pred),
        # filter1
        PredInferByAttrs(la_join0.right_rel.attrs, filter0.pred),
        # relation
        RelEq(la_join0.left_rel, la_join1.left_rel),
        RelEq(la_join0.right_rel, filter0.rel),
    ]
)

