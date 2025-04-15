from trans.plan.operator.impl.filter import Filter
from trans.rule.constraint.impl.has_const import HasConst
from trans.rule.constraint.impl.pred_infer_by_const import PredInferByConst
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

filter0 = Filter()
p_src = filter0


filter1 = Filter()
p_dst = filter1

InferFilterFromConstraints = Rule(
    "InferFilterFromConstraints",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        HasConst(filter0.pred),
    ],
    trans_constraints=[
        # filter1
        PredInferByConst(filter0.pred, filter1.pred),
        # relation
        RelEq(filter0.rel, filter1.rel),
    ]
)

