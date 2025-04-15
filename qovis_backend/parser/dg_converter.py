import json
import os
import re
import sys
from typing import Dict, List, Optional

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from common.dynamic_graph import DynamicGraph
from common.plan import Plan, PlanNode, PlanEdge, RuleMeta, StrategyMeta, SoftTransMeta
from utils.id_counter import IdCounter


class DgConverter:
    def __init__(self, records: List[Dict]):
        self.records = records

        self.pid_counter = IdCounter()

        self.vid_counter = IdCounter()
        self.vid_dict: Dict[str, int] = {}  # simple_str -> id

        self.batch_id_dict = {}
        self.batch_id_counter = IdCounter()

        self.dg: Optional[DynamicGraph] = None

    def get(self) -> DynamicGraph:
        return self.dg

    def exec(self):
        self.filter_records()
        self.clean_plan(self.records)
        self.extract()

    def filter_records(self):
        last_idx = -1
        for i, r in enumerate(self.records):
            if 'CreateViewCommand' in json.dumps(r):
                last_idx = i
            if r['rType'] == 'pruned' and last_idx == i - 1:
                last_idx = i
        self.records = self.records[last_idx + 1:]

    def extract(self):
        self.dg = DynamicGraph()

        self.refine_records()

        # extract block first
        # in each block, one plan in, one plan out

        block_identifier_dict = {
            'rule': 0,
            'strategy': 1,
            'pruned': 1,
        }

        dividers = []
        # indicates the pos after records[i]
        for possible_div in range(1, len(self.records)):
            p = self.records[possible_div - 1]
            q = self.records[possible_div]
            if block_identifier_dict[p['rType']] != block_identifier_dict[q['rType']]:
                dividers.append(possible_div)

        blocks = []
        dividers = [0] + dividers + [len(self.records)]
        for i in range(len(dividers) - 1):
            start = dividers[i]
            end = dividers[i + 1]
            blocks.append(self.records[start: end])

        # create the dag structure

        assert blocks[0][0]['rType'] == 'rule'

        for block in blocks:
            if block[0]['rType'] == 'rule':
                # is a rule executor block
                self.process_rule_block(block)

            elif block[0]['rType'] == 'strategy':
                # is a strategy planner block
                invoke_groups = {}
                for record in block:
                    invoke_groups.setdefault(record['invokeCnt'], []).append(record)
                sorted_items = list(invoke_groups.items())
                sorted_items.sort(key=lambda x: x[0])
                for _, b in sorted_items:
                    self.process_strategy_block(b)

            else:
                raise Exception("Unknown record type " + block[0]['rType'])

        self.refine_plans()
        self.filter_plans()

    def refine_records(self):
        # change FinishAnalysis
        for r in self.records:
            if r['rType'] != 'rule' or 'FinishAnalysis' not in r['ruleName']:
                continue
            assert r['type'] == 'optimizer rule'
            r['type'] = 'analysis rule'

    def process_rule_block(self, block: List[Dict]):
        for idx, record in enumerate(block):
            rule_meta = RuleMeta()
            rule_meta.type = record['type']
            rule_meta.name = record['ruleName']
            rule_meta.effective = True
            rule_meta.run_time = record['runTime']
            rule_meta.class_name = record['className']
            rule_meta.batch_name = record['batchName']

            batch_id = record['batchId']
            if batch_id in self.batch_id_dict:
                batch_id = self.batch_id_dict[batch_id]
            else:
                batch_id = self.batch_id_dict \
                    .setdefault(batch_id, self.batch_id_counter.get())
            rule_meta.batch_id = batch_id

            src = record['oldPlan']
            src.meta = rule_meta

            dst = record['newPlan']
            dst.meta = rule_meta

            self.dg.plans.append(src)
            self.dg.plans.append(dst)

    def process_strategy_block(self, block: List[Dict]):
        prune_list = list(filter(lambda r: r['rType'] == 'pruned', block))

        # non_prune_list = list(filter(lambda r: r['rType'] != 'pruned', block))
        # rid_to_child_rid_list = {}
        # for record in non_prune_list:
        #     child_rid_list = rid_to_child_rid_list.setdefault(record['rid'], [])
        #     child_rid_list += record['childRidSeq']

        selected_rid_set = set()
        for prune in prune_list:
            selected_rid_set.add(prune['rid'])
            selected_rid_set.add(prune['selectedRid'])

        filtered_records = list(filter(lambda r: r['rType'] != 'pruned' and r['rid'] in selected_rid_set,
                                       block))

        plans: List[Plan] = []

        for idx, record in enumerate(filtered_records):
            for output_plan in record['physicalPlans']:
                strategy_meta = StrategyMeta()
                strategy_meta.type = record['type']
                strategy_meta.name = record['strategyName']
                strategy_meta.effective = True
                strategy_meta.run_time = record['runTime']
                strategy_meta.class_name = record['className']
                strategy_meta.invoke_cnt = record['invokeCnt']
                strategy_meta.rid = record['rid']

                src = record['logicalPlan']
                src.meta = strategy_meta

                dst = output_plan
                dst.meta = strategy_meta

                plans.append(src)
                plans.append(dst)

        # complete plans

        new_plans = []
        plan_model = None
        for idx in range(0, len(plans), 2):
            src, dst = plans[idx], plans[idx + 1]
            if plan_model is not None and plan_model.contain_plan_later():
                # need extend
                # find placeholder (corresponding node in plan_model)
                target_root = plan_model.node_dict[src.root.vid]
                assert (target_root is not None and target_root.plan_later is not None)
                # replace this placeholder to get two complete plans
                src2 = self.merge_plan(plan_model, target_root, src)
                dst2 = self.merge_plan(plan_model, target_root, dst)
            else:
                src2, dst2 = src, dst
            new_plans.append(src2)
            new_plans.append(dst2)
            plan_model = dst2

        # # child_rid -> parent_rid
        # parent_rid_dict = {prune['selectedRid']: prune['rid'] for prune in prune_list}
        # # rid -> list of plans
        # rid_to_plans = {}
        # for plan in plans:
        #     assert isinstance(plan.meta, StrategyMeta)
        #     rid_to_plans.setdefault(plan.meta.rid, []).append(plan)
        #
        # pid_to_new_plan = {}
        # for plan in plans:
        #     if not any([node.plan_later is not None for node in plan.node_dict.values()]):
        #         continue
        #     # has placeholder
        #     rid = plan.meta.rid
        #     child_plans = rid_to_plans[child_rid_dict[rid]]

        for plan in new_plans:
            self.dg.plans.append(plan)

    @staticmethod
    def merge_plan(plan_with_placeholder: Plan, plan_later_node: PlanNode, target: Plan) -> Plan:
        if plan_with_placeholder.root == plan_later_node:
            return target

        # copy plan
        new_plan = plan_with_placeholder.copy()
        new_plan.pid = target.pid
        new_plan.meta = target.meta

        # use plan_late_node in the copy
        plan_later_node = new_plan.node_dict[plan_later_node.vid]

        # clean new_plan

        assert len(plan_later_node.consumers) == 1
        link_node = plan_later_node.consumers[0]
        # cache position of original node
        idx_cache = link_node.providers.index(plan_later_node)

        nodes_to_remove = []

        def collect(x: PlanNode):
            nodes_to_remove.append(x)
            for y in x.providers:
                collect(y)

        collect(plan_later_node)

        for node_remove in nodes_to_remove:
            del new_plan.node_dict[node_remove.vid]
            # only delete cur -> consumer, as all edge can be removed
            for c in node_remove.consumers:
                del new_plan.edge_dict[PlanEdge.get_eid(node_remove, c)]

        # link target plan to new plan, replacing subtree from plan_later_node
        # target_copy_root -> link_node

        target_copy = target.copy()

        # first update relation in target plan
        new_plan.node_dict.update(target_copy.node_dict)
        new_plan.edge_dict.update(target_copy.edge_dict)

        target_copy_root = target_copy.root  # is the replacement of plan_later_node

        # add edge
        link_edge = PlanEdge(target_copy_root, link_node)
        new_plan.edge_dict[link_edge.eid] = link_edge
        # add node dependency
        assert len(target_copy_root.consumers) == 0
        target_copy_root.consumers.append(link_node)
        link_node.providers[idx_cache] = target_copy_root
        assert link_node.providers[idx_cache] is target_copy_root

        return new_plan

    def clean_plan(self, records: List[Dict]):
        for r in records:
            for f in ['oldPlan', 'newPlan', 'logicalPlan']:
                if f in r:
                    r[f] = self.parse_plan(r[f])
            for f in ['physicalPlans']:
                if f in r:
                    r[f] = [self.parse_plan(p) for p in r[f]]

    def parse_plan(self, raw_plan: List[Dict]) -> Plan:
        plan = Plan(self.pid_counter.get())

        # parse plan nodes

        nodes = []
        child_cnt_list = []
        for r_node in raw_plan:
            name = r_node['node-name']
            str_ = r_node['str']
            plan_later = r_node.get('plan-later')
            addr = r_node['addr']

            if re.fullmatch(r"[a-zA-Z\s\']+", str_):
                addr_str = str(addr)
                if addr_str in self.vid_dict:
                    vid = self.vid_dict[addr_str]
                else:
                    vid = self.vid_counter.get()
                    self.vid_dict[addr_str] = vid
            else:
                if str_ in self.vid_dict:
                    vid = self.vid_dict[str_]
                else:
                    vid = self.vid_counter.get()
                    self.vid_dict[str_] = vid

            nodes.append(PlanNode(name, vid, str_, addr, plan_later))
            child_cnt_list.append(r_node['num-children'])

        plan.root = nodes[0]
        for node in nodes:
            plan.node_dict[node.vid] = node

        # reconstruct plan structure

        node_stack = [nodes[0]]
        child_cnt_stack = [child_cnt_list[0]]

        for i in range(1, len(nodes)):
            provider = nodes[i]

            while child_cnt_stack[-1] == 0:
                node_stack.pop()
                child_cnt_stack.pop()
            consumer = node_stack[-1]
            child_cnt_stack[-1] -= 1

            # create edge

            consumer.providers.append(provider)
            provider.consumers.append(consumer)

            edge = PlanEdge(provider, consumer)
            plan.edge_dict[edge.eid] = edge

            # add cur node

            node_stack.append(provider)
            child_cnt_stack.append(child_cnt_list[i])

        return plan

    def refine_plans(self):
        plans = self.dg.plans

        # remove row data resolve
        plans = list(filter(lambda p: not (p.meta.name == 'Analyzer$ResolveDeserializer'
                                           and 'org.apache.spark.sql.Row' in p.root.str_),
                            plans))

        # remove adaptive plan convert
        new_plans = []
        for i in range(0, len(plans), 2):
            p = plans[i + 1]
            if p.meta.name == 'adaptive.InsertAdaptiveSparkPlan' and len(p.node_dict) == 1:
                continue
            new_plans += plans[i: i + 2]
        plans = new_plans

        # remove return ans
        for p in plans:
            if p.root.name != "ReturnAnswer":
                continue
            assert len(p.root.providers) == 1
            new_root = p.root.providers[0]
            new_root.consumers = []
            del p.node_dict[p.root.vid]
            del p.edge_dict[PlanEdge.get_eid(new_root, p.root)]
            p.root = new_root

        # complete some execution adaptive rules
        name_set = {'adaptive.OptimizeShuffleWithLocalRead', 'CollapseCodegenStages'}
        for i in range(2, len(plans), 2):
            # p is the last completed plan
            p, p0, p1 = plans[i - 1], plans[i], plans[i + 1]
            if p0.meta.name not in name_set:
                continue
            if p0.root.vid not in p.node_dict:
                sys.stderr.write(f"Can't fine-tune adaptive rule {p0.meta.name} with index {i}\n")
                continue
            root_node = p.node_dict[p0.root.vid]
            plans[i] = self.merge_plan(p, root_node, p0)
            plans[i + 1] = self.merge_plan(p, root_node, p1)

        self.dg.plans = plans

    def filter_plans(self):
        plans = self.dg.plans

        new_plans = [plans[0]]
        for i in range(len(plans) - 1):
            p0 = plans[i]
            p1 = plans[i + 1]
            if p0.equals(p1):
                if i & 1 == 0:
                    # plan doesn't change
                    # sys.stderr.write(f'Non-effective rule detected. {p1.meta.name}@{i}\n')
                    new_plans.append(p1)
                else:
                    # between two rules
                    # don't add p1
                    continue
            else:
                if i & 1 == 0:
                    # normal case, plan is changed by rule
                    new_plans.append(p1)
                else:
                    # plan is changed by other reason
                    new_plans.append(p1)
                    p1.meta = SoftTransMeta()

        self.dg.plans = new_plans

