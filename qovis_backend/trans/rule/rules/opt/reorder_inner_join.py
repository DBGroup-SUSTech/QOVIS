from trans.plan.operator.impl.inner_join import InnerJoin
from trans.rule.constraint.impl.pred_eq import PredEq
from trans.rule.constraint.impl.pred_size_le import PredSizeLe
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule

# both p_src and p_dst are left-deep trees

#    join0
#    /   \
# join1  None
join0 = InnerJoin()
join1 = InnerJoin()
p_src = join0\
    .add_child(join1)\
    .add_child(None)

#    join2
#    /   \
# join3  None
join2 = InnerJoin()
join3 = InnerJoin()
p_dst = join2\
    .add_child(join3)\
    .add_child(None)

ReorderInnerJoin = Rule(
    "ReorderInnerJoin",
    Rule.OPT, p_src, p_dst,
    src_constraints=[
        # we only consider empty predicates
        PredSizeLe(join0.pred, 0),
        PredSizeLe(join1.pred, 0),
    ],
    trans_constraints=[
        # join2 & join3, all predicates are empty
        PredEq(join0.pred, join2.pred),
        PredEq(join1.pred, join3.pred),
        # relation
        #       join0       join2
        #       /   \       /   \
        #    join1  C    join3  B
        #    /   \       /   \
        #    A   B       A   C
        RelEq(join1.left_rel, join3.left_rel),
        RelEq(join0.right_rel, join3.right_rel),
        RelEq(join1.right_rel, join2.right_rel),
    ]
)

