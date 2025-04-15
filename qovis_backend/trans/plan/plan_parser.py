import sys

from entity.plan import Plan as RawPlan
from entity.plan import PlanNode as RawPlanNode
from trans.plan.operator.custom_op0 import CustomOp0
from trans.plan.operator.custom_op1 import CustomOp1
from trans.plan.operator.custom_op2 import CustomOp2
from trans.plan.operator.impl.deduplicate import Deduplicate
from trans.plan.operator.impl.external_rdd import ExternalRdd
from trans.plan.operator.impl.in_mem_rel import InMemoryRelation
from trans.plan.operator.impl.inner_join import InnerJoin
from trans.plan.operator.impl.left_anti_join import LeftAntiJoin
from trans.plan.operator.impl.aggregate import Aggregate
from trans.plan.operator.impl.filter import Filter
from trans.plan.operator.impl.left_outer_join import LeftOuterJoin
from trans.plan.operator.impl.left_semi_join import LeftSemiJoin
from trans.plan.operator.impl.local_relation import LocalRelation
from trans.plan.operator.impl.local_table_scan import LocalTableScan
from trans.plan.operator.impl.project import Project
from trans.plan.operator.impl.resolved_hint import ResolvedHint
from trans.plan.operator.impl.serialize_from_object import SerializeFromObject
from trans.plan.operator.impl.sort import Sort
from trans.plan.operator.impl.subquery_alias import SubqueryAlias
from trans.plan.operator.impl.unresolved_hint import UnresolvedHint
from trans.plan.operator.impl.unresolved_relation import UnresolvedRelation
from trans.plan.operator.impl.view import View
from trans.plan.query_plan import QueryPlan as TypedPlan
from trans.plan.plan_node import PlanNode as TypedPlanNode


class PlanParser:
    MAPPING = {
        'org.apache.spark.sql.catalyst.plans.logical.Project': Project,
        'org.apache.spark.sql.execution.columnar.InMemoryRelation': InMemoryRelation,
        # Join is processed specially
        'org.apache.spark.sql.catalyst.plans.logical.Filter': Filter,
        'org.apache.spark.sql.catalyst.plans.logical.SerializeFromObject': SerializeFromObject,
        'org.apache.spark.sql.execution.ExternalRDD': ExternalRdd,
        'org.apache.spark.sql.catalyst.plans.logical.Aggregate': Aggregate,
        'org.apache.spark.sql.catalyst.plans.logical.Sort': Sort,
        'org.apache.spark.sql.catalyst.plans.logical.SubqueryAlias': SubqueryAlias,
        'org.apache.spark.sql.catalyst.plans.logical.View': View,
        'org.apache.spark.sql.catalyst.plans.logical.LocalRelation': LocalRelation,
        'org.apache.spark.sql.catalyst.plans.logical.Deduplicate': Deduplicate,
        # org.apache.spark.sql.catalyst.plans.logical.Subquery	Subquery,
        'org.apache.spark.sql.catalyst.plans.logical.UnresolvedHint': UnresolvedHint,
        'org.apache.spark.sql.catalyst.plans.logical.ResolvedHint': ResolvedHint,
        'org.apache.spark.sql.execution.LocalTableScanExec': LocalTableScan,
        'org.apache.spark.sql.catalyst.analysis.UnresolvedRelation' : UnresolvedRelation,
    }

    def parse(self, plan: RawPlan) -> TypedPlan:
        res = TypedPlan(plan.pid)

        plan_root = self._parse_node(res, plan.root)
        res.root = plan_root
        # res.init()
        try:
            res.init()
        except Exception as e:
            sys.stderr.write(f"Cannot resolve plan {plan.pid}: {e}\n")

        nodes = []
        self._collect(plan_root, nodes)
        new_vid = 0
        for node in nodes:
            node.vid = new_vid
            res.node_dict[node.vid] = node
            new_vid += 1

        res.labels = plan.labels.copy()

        return res

    def _parse_node(self, res_plan: TypedPlan, node: RawPlanNode) -> TypedPlanNode:
        res = self._parse_node0(node)
        res.assign(res_plan, node.vid, node.clazz, node.str_, node.addr)
        res.children = [self._parse_node(res_plan, c) for c in node.providers]
        return res

    def _collect(self, node: TypedPlanNode, res: list[TypedPlanNode]):
        res.append(node)
        for child in node.children:
            self._collect(child, res)

    def _parse_node0(self, node: RawPlanNode) -> TypedPlanNode:
        clazz = node.clazz
        if clazz in PlanParser.MAPPING:
            return PlanParser.MAPPING[clazz]()

        if clazz == 'org.apache.spark.sql.catalyst.plans.logical.Join':
            s = node.str_
            if 'Inner' in s:
                return InnerJoin()
            elif 'LeftAnti' in s:
                return LeftAntiJoin()
            elif 'LeftSemi' in s:
                return LeftSemiJoin()
            elif 'LeftOuter' in s:
                return LeftOuterJoin()
            else:
                raise Exception('Unknown join type: %s' % s)

        # custom operator
        n_child = len(node.providers)
        if n_child == 0:
            return CustomOp0().set_name(node.name)
        elif n_child == 1:
            return CustomOp1().set_name(node.name)
        elif n_child == 2:
            return CustomOp2().set_name(node.name)
        else:
            raise Exception('Unknown custom operator: %s' % node.name)
