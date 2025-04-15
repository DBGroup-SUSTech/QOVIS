from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.join_like import JoinLike
from trans.rule.constraint.impl.pred_size_ge import PredSizeGe
from trans.rule.constraint.impl.pred_split import PredSplit
from trans.rule.constraint.impl.pred_split_by_attrs import PredSplitByAttrs
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.constraint.impl.sub_attrs import SubAttrs
from trans.rule.rule import Rule


join0 = JoinLike()
p_src = join0


join1 = JoinLike().bind(join0)
filter0 = Filter()
p_dst = join1 \
    .add_child(None)\
    .add_child(filter0)

# ExpandFilterFromJoinRight = Rule(
#     "ExpandFilterFromJoinRight",
#     Rule.OPT, p_src, p_dst,
#     src_constraints=[
#         PredSizeGe(join0.pred, 1),
#     ],
#     trans_constraints=[
#         # join1 type
#         # OpTypeEq(join1, join0),
#         # join1 & filter0
#         PredSplit(join0.pred, join1.pred, filter0.pred),
#         # relation
#         RelEq(join0.left_rel, join1.left_rel),
#         RelEq(join0.right_rel, filter0.rel),
#     ],
#     dst_constraints=[
#         # attrs of filter0's predicate are a subset of its relation attrs
#         SubAttrs(filter0.pred.attrs, filter0.rel.attrs),
#     ]
# )

ExpandFilterFromJoinRight = Rule(
    "ExpandFilterFromJoinRight",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        PredSizeGe(join0.pred, 1),
    ],
    trans_constraints=[
        # join1 type
        # OpTypeEq(join1, join0),
        # join1 & filter0
        PredSplitByAttrs(join0.pred, filter0.pred, join0.right_rel.attrs, join1.pred),
        # relation
        RelEq(join0.left_rel, join1.left_rel),
        RelEq(join0.right_rel, filter0.rel),
    ],
)

