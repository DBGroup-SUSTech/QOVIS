from trans.rule.rules.opt.collapse_filter import CollapseFilter
from trans.rule.rules.opt.collapse_filter_to_join import CollapseFilterToJoin
from trans.rule.rules.opt.collapse_project import CollapseProject
from trans.rule.rules.opt.convert_to_local_relation import ConvertToLocalRelation
from trans.rule.rules.opt.ensure_attrs_order import EnsureAttrsOrder
from trans.rule.rules.opt.exchange_filter import ExchangeFilter
from trans.rule.rules.opt.exchange_inner_join_children import ExchangeInnerJoinChildren
from trans.rule.rules.opt.expand_filter import ExpandFilter
from trans.rule.rules.opt.expand_filter_from_join_left import ExpandFilterFromJoinLeft
from trans.rule.rules.opt.expand_filter_from_join_right import ExpandFilterFromJoinRight
from trans.rule.rules.opt.expand_filter_from_join_top import ExpandFilterFromJoinTop
from trans.rule.rules.opt.infer_filter_from_constraints import InferFilterFromConstraints
from trans.rule.rules.opt.infer_filter_from_left_anti_join import InferFilterFromLeftAntiJoin
from trans.rule.rules.opt.prune_columns_aggregate import PruneColumnsAggregate
from trans.rule.rules.opt.prune_columns_join_left import PruneColumnsJoinLeft
from trans.rule.rules.opt.prune_columns_join_right import PruneColumnsJoinRight
from trans.rule.rules.opt.prune_object_serializer import PruneObjectSerializer
from trans.rule.rules.opt.push_down_expressions_join_left import PushDownExpressionsJoinLeft
from trans.rule.rules.opt.push_down_left_semi_anti_join import PushDownLeftSemiAntiJoinLeft
from trans.rule.rules.opt.push_down_predicates_join_left import PushDownPredicatesJoinLeft
from trans.rule.rules.opt.push_down_predicates_join_right import PushDownPredicatesJoinRight
from trans.rule.rules.opt.push_down_predicates_project import PushDownPredicatesProject
from trans.rule.rules.opt.remove_alias import RemoveAlias
from trans.rule.rules.opt.remove_noop_project import RemoveNoopProject
from trans.rule.rules.opt.reorder_inner_join import ReorderInnerJoin

RULE_LIST = [
    CollapseFilter,
    CollapseFilterToJoin,
    CollapseProject,
    ConvertToLocalRelation,
    EnsureAttrsOrder,
    ExchangeFilter,
    ExchangeInnerJoinChildren,
    # ExpandFilter,
    ExpandFilterFromJoinLeft,
    ExpandFilterFromJoinRight,
    # ExpandFilterFromJoinTop,
    InferFilterFromConstraints,
    InferFilterFromLeftAntiJoin,
    PruneColumnsAggregate,
    PruneColumnsJoinLeft,
    PruneColumnsJoinRight,
    PruneObjectSerializer,
    PushDownExpressionsJoinLeft,
    PushDownLeftSemiAntiJoinLeft,
    PushDownPredicatesJoinLeft,
    PushDownPredicatesJoinRight,
    PushDownPredicatesProject,
    RemoveAlias,
    RemoveNoopProject,
    ReorderInnerJoin,
]

REORDER_RULE_LIST = [
    ExchangeInnerJoinChildren,
    ReorderInnerJoin,
]

NORMAL_RULE_LIST = [r for r in RULE_LIST if r not in REORDER_RULE_LIST]

RULE_DICT = {rule.name: rule for rule in RULE_LIST}
