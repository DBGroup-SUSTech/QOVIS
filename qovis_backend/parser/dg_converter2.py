import json
import os
import re
import sys
from enum import Enum
from typing import Dict, List, Optional

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from common.dynamic_graph import DynamicGraph
from common.plan import Plan, PlanNode, PlanEdge, RuleMeta, StrategyMeta, SoftTransMeta, ActionMeta, EvolutionLabel
from utils.id_counter import IdCounter


class RType(Enum):
    ACTION = 'action'
    INFO = 'info'


class DataType(Enum):
    # action
    STRATEGY = 'strategy'

    # info
    ACTION = 'action'
    JOIN_SEL = 'join sel'
    DY_JOIN_SEL = 'dy join sel'
    PHASE = 'phase'
    PRUNED = 'pruned'
    AQE_START = 'aqe start'
    AQE_END = 'aqe end'
    LABEL = 'label'
    STAGE = 'stage'


class Assign(Enum):
    BEFORE = 'before'
    AFTER = 'after'
    INDIVIDUAL = 'ind'


class DgConverter2:
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
        self.comp_evo_label()

    def filter_records(self):
        last_idx = -1
        for i, r in enumerate(self.records):
            if 'CreateViewCommand' in json.dumps(r):
                last_idx = i
            if r['type'] == DataType.PRUNED.value and last_idx == i - 1:
                last_idx = i
        self.records = self.records[last_idx + 1:]

    def extract(self):
        self.dg = DynamicGraph()

        self.assign_info_records()
        self.refine_records()

        # extract block first
        # in each block, one plan in, one plan out

        dividers = []
        block_names = []

        for idx, r in enumerate(self.records):
            phase_info_lst = self.get_info_by_data_type(r, DataType.PHASE)
            if len(phase_info_lst) > 0 and phase_info_lst[0]['phaseFlag'] == 'start':
                dividers.append(idx)
                block_names.append(phase_info_lst[0]['phaseName'])
                continue

        blocks = []
        dividers = dividers + [len(self.records)]
        for i in range(len(dividers) - 1):
            start = dividers[i]
            end = dividers[i + 1]
            if start >= end:
                continue
            blocks.append(self.records[start: end])

        # create the dag structure

        for idx, block in enumerate(blocks):
            phase_name = block_names[idx]
            # remove phase info record
            block = list(filter(lambda r: r['type'] != 'phase', block))
            if len(block) == 0:
                continue

            if phase_name in ['analysis', 'optimization']:
                # is a rule executor block
                self.process_normal_rule_block(block)

            elif phase_name == 'planning':
                if block[0].get('name') == 'InsertReturnAnswer':
                    self.process_strategy_block(block)
                else:
                    self.process_normal_rule_block(block)

            elif phase_name == 'aqe':
                self.process_execution_block(block)

            else:
                raise Exception("Unknown record phase block: " + phase_name)

        self.refine_plans()
        self.filter_plans()

    def assign_info_records(self):
        def last_action(start) -> Optional[Dict]:
            j = start
            while j >= 0:
                tmp_r = self.records[j]
                if tmp_r['rType'] == RType.ACTION.value:
                    return tmp_r
                j -= 1
            return None

        def next_action(start) -> Optional[Dict]:
            j = start
            while j < len(self.records):
                tmp_r = self.records[j]
                if tmp_r['rType'] == RType.ACTION.value:
                    return tmp_r
                j += 1
            return None

        for i in range(len(self.records)):
            r = self.records[i]
            if r['rType'] != RType.INFO.value:
                if 'info' not in r:
                    r['info'] = []
                continue
            if r['assign'] == Assign.BEFORE.value:
                tmp = last_action(i - 1)
                assert tmp is not None
                tmp.setdefault('info', []).append(r)
            elif r['assign'] == Assign.AFTER.value:
                tmp = next_action(i + 1)
                assert tmp is not None
                tmp.setdefault('info', []).append(r)
            else:
                sys.stderr.write(f'Unknown info record {str(r)}\n')

        self.records = list(filter(lambda x: x['rType'] == RType.ACTION.value, self.records))

    def get_info_by_data_type(self, record: Dict, data_type: DataType) -> List[Dict]:
        lst = list(filter(lambda x: x['type'] == data_type.value, record['info']))
        return lst

    def split_info(self, info_lst) -> [List, List]:
        def is_before(x):
            return (x['type'] == DataType.PHASE.value and x['phaseFlag'] == 'start') \
                   or (x['type'] == DataType.AQE_START) \
                   or (x['type'] == DataType.LABEL.value and x['label'] == 'AQE Re-optimizing')
        before = list(filter(lambda x: is_before(x), info_lst))
        after = list(filter(lambda x: x not in before, info_lst))
        return [before, after]

    def refine_records(self):
        # change FinishAnalysis
        for idx in range(len(self.records)):
            r = self.records[idx]
            if r['type'] == 'optimizer rule' and 'FinishAnalysis' in r['ruleName']:
                assert idx >= 1
                last_r = self.records[idx - 1]
                info_lst = self.get_info_by_data_type(r, DataType.PHASE)
                info_last_lst = self.get_info_by_data_type(last_r, DataType.PHASE)

                assert len(info_lst) == 1
                assert len(info_last_lst) == 1

                info = info_lst[0]
                info_last = info_last_lst[0]

                assert info_last['phaseFlag'] == 'end' and info_last['phaseName'] == 'analysis'
                assert info['phaseFlag'] == 'start' and info['phaseName'] == 'optimization'

                # update
                r['type'] = 'analysis rule'

                last_r['info'].remove(info_last)
                r['info'].remove(info)

                r['info'].append(info_last)
                self.records[idx + 1]['info'].append(info)


    def process_normal_rule_block(self, block: List[Dict]) -> (int, int):
        start = end = len(self.dg.plans)
        for idx, record in enumerate(block):
            if record['type'] == DataType.ACTION.value:
                rule_meta = ActionMeta()
                rule_meta.name = record['name']
            else:
                assert record['type'].endswith('rule')
                rule_meta = RuleMeta()
                rule_meta.name = record['ruleName']
                rule_meta.run_time = record['runTime']
                rule_meta.class_name = record['className']

            rule_meta.type = record['type']
            rule_meta.effective = True
            rule_meta.batch_name = record['batchName']

            batch_id = record['batchId']
            if batch_id in self.batch_id_dict:
                batch_id = self.batch_id_dict[batch_id]
            else:
                batch_id = self.batch_id_dict \
                    .setdefault(batch_id, self.batch_id_counter.get())
            rule_meta.batch_id = batch_id

            before, after = self.split_info(record['info'])

            src = record['oldPlan']
            src.meta = rule_meta
            src.events = before

            dst = record['newPlan']
            dst.meta = rule_meta
            dst.events = after

            self.dg.plans.append(src)
            self.dg.plans.append(dst)
            end += 2
        return start, end

    def process_execution_block(self, block: List[Dict]):
        # remove resolution action
        block = list(filter(lambda r: not (r['type'] == 'analysis rule' and r['batchName'] == 'Resolution'), block))

        # bind info to actions
        # for idx, r in enumerate(block):
        #     if r['rType'] == RType.ACTION.value:
        #         continue
        #     if r['type'] == DataType.JOIN_SEL.value:
        #         if idx + 1 >= len(block) or 'SparkStrategies$JoinSelection$' != block[idx + 1].get('strategyName'):
        #             print('Inefficient JoinSelection record')
        #             continue
        #         action = block[idx + 1]
        #         action['info_list'] = [r]
        #     elif r['type'] == DataType.DY_JOIN_SEL.value:
        #         if idx + 1 >= len(block) or 'DynamicJoinSelection' != block[idx + 1].get('ruleName'):
        #             print('Inefficient DynamicJoinSelection record')
        #             continue
        #         action = block[idx + 1]
        #         action['info_list'] = [r]
        #     elif r['type'] == 'aqe start':
        #         action = block[idx + 1]
        #         action['aqe_start'] = True
        #     elif r['type'] in [DataType.PHASE.value, DataType.PRUNED.value, 'aqe end']:
        #         pass
        #     else:
        #         raise Exception("Unknown info record: " + r['type'])

        # check assigned info
        for idx, r in enumerate(block):
            for info in r['info']:
                if info['type'] == DataType.JOIN_SEL.value:
                    if 'SparkStrategies$JoinSelection$' == r.get('strategyName'):
                        continue
                    print('Inefficient JoinSelection record')
                    r['info'].remove(info)
                elif info['type'] == DataType.DY_JOIN_SEL.value:
                    if 'DynamicJoinSelection' == r.get('ruleName'):
                        continue
                    print('Inefficient DynamicJoinSelection record')
                    r['info'].remove(info)
                elif info['type'] in [DataType.PHASE.value, DataType.PRUNED.value,
                                   DataType.AQE_START.value, DataType.AQE_END.value,
                                   DataType.LABEL.value, DataType.STAGE.value]:
                    pass
                else:
                    raise Exception("Unknown info record: " + info['type'])

        # remove processed info record
        block = list(filter(lambda r: r['rType'] == RType.ACTION.value
                                      or r['type'] == DataType.PRUNED.value, block))

        # divide sub-blocks
        dividers = []
        in_planning_block = False
        for idx, r in enumerate(block):
            if r.get('name') == 'InsertReturnAnswer':
                assert not in_planning_block
                dividers.append(idx + 1)
                in_planning_block = True
            elif in_planning_block and r['type'] != DataType.STRATEGY.value:
                dividers.append(idx)
                in_planning_block = False

        sub_blocks = []
        dividers = [0] + dividers + [len(block)]
        for i in range(len(dividers) - 1):
            start = dividers[i]
            end = dividers[i + 1]
            if start >= end:
                continue
            sub_blocks.append(block[start: end])

        for sb in sub_blocks:
            if len(sb) == 0:
                continue
            first_r = sb[0]

            if first_r['type'] != DataType.STRATEGY.value:
                # is a rule executor block
                start, end = self.process_normal_rule_block(sb)
            else:
                start, end = self.process_strategy_block(sb)

    def process_strategy_block(self, block: List[Dict]) -> (int, int):
        if block[0].get('name') == 'InsertReturnAnswer':
            self.process_normal_rule_block([block[0]])
            block = block[1:]

        prune_list = []
        for r in block:
            for info in r['info']:
                if info['type'] == DataType.PRUNED.value:
                    prune_list.append(info)

        # non_prune_list = list(filter(lambda r: r['rType'] != 'pruned', block))
        # rid_to_child_rid_list = {}
        # for record in non_prune_list:
        #     child_rid_list = rid_to_child_rid_list.setdefault(record['rid'], [])
        #     child_rid_list += record['childRidSeq']

        selected_rid_set = set()
        for prune in prune_list:
            selected_rid_set.add(prune['rid'])
            selected_rid_set.add(prune['selectedRid'])

        plans: List[Plan] = []
        start = end = len(self.dg.plans)

        for idx, record in enumerate(block):
            for output_plan in record['physicalPlans']:
                strategy_meta = StrategyMeta()
                strategy_meta.type = record['type']
                strategy_meta.name = record['strategyName']
                strategy_meta.effective = True
                strategy_meta.run_time = record['runTime']
                strategy_meta.class_name = record['className']
                strategy_meta.invoke_cnt = record['invokeCnt']
                strategy_meta.rid = record['rid']

                before, after = self.split_info(record['info'])

                src = record['logicalPlan']
                src.meta = strategy_meta
                src.events = before

                dst = output_plan
                dst.meta = strategy_meta
                dst.events = after

                plans.append(src)
                plans.append(dst)
                end += 2

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

        # clean pruned info
        for plan in new_plans:
            plan.info_list = list(filter(lambda x: x['type'] != DataType.PRUNED.value, plan.info_list))

        assert len(new_plans) == len(plans)
        for plan in new_plans:
            self.dg.plans.append(plan)

        return start, end

    @staticmethod
    def merge_plan(plan_with_placeholder: Plan, plan_later_node: PlanNode, target: Plan) -> Plan:
        if plan_with_placeholder.root == plan_later_node:
            return target

        # copy plan
        new_plan = plan_with_placeholder.copy()
        new_plan.pid = target.pid
        new_plan.meta = target.meta
        new_plan.events = target.info_list

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
            for f in ['oldPlan', 'newPlan', 'logicalPlan', 'physicalPlan', 'plan']:
                if f in r:
                    r[f] = self.parse_plan(r[f])
            for f in ['physicalPlans', 'stages']:
                if f in r:
                    r[f] = [self.parse_plan(p) for p in r[f]]

    def parse_plan(self, raw_plan: List[Dict]) -> Plan:
        plan = Plan(self.pid_counter.get())

        # parse plan nodes

        nodes = []
        child_cnt_list = []
        local_vid_dict = {}
        for r_node in raw_plan:
            name = r_node['node-name']
            str_ = r_node['str']
            plan_later = r_node.get('plan-later')
            addr = r_node['addr']

            if re.fullmatch(r"[a-zA-Z\s\']+", str_) or 'Deduplicate' in str_ or 'SubqueryAlias' in str_ or 'View' in str_ or 'Aggregate' in str_ \
                    or 'LocalRelation' in str_:
                addr_str = str(addr)
                if addr_str in self.vid_dict:
                    vid = self.vid_dict[addr_str]
                else:
                    vid = self.vid_counter.get()
                    local_vid_dict[addr_str] = vid
            else:
                if str_ in self.vid_dict:
                    vid = self.vid_dict[str_]
                else:
                    vid = self.vid_counter.get()
                    local_vid_dict[str_] = vid

            nodes.append(PlanNode(name, vid, str_, addr, plan_later))
            child_cnt_list.append(r_node['num-children'])

        self.vid_dict.update(local_vid_dict)

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
        # for p in plans:
        #     if p.root.name != "ReturnAnswer":
        #         continue
        #     assert len(p.root.providers) == 1
        #     new_root = p.root.providers[0]
        #     new_root.consumers = []
        #     del p.node_dict[p.root.vid]
        #     del p.edge_dict[PlanEdge.get_eid(new_root, p.root)]
        #     p.root = new_root

        # complete some execution adaptive rules
        name_set = {'adaptive.OptimizeShuffleWithLocalRead', 'CollapseCodegenStages',
                    'adaptive.CoalesceShufflePartitions'}
        for i in range(2, len(plans), 2):
            # p is the last completed plan
            p, p0, p1 = plans[i - 1], plans[i], plans[i + 1]
            if p0.meta.name not in name_set:
                continue
            if p0.root.vid not in p.node_dict:
                if p0.root.name == 'ShuffleExchange':
                    continue        # result stage, don't need to complete
                sys.stderr.write(f"Can't fine-tune adaptive rule {p0.meta.name} with index {i}\n")
                continue
            root_node = p.node_dict[p0.root.vid]
            plans[i] = self.merge_plan(p, root_node, p0)
            plans[i + 1] = self.merge_plan(p, root_node, p1)

        self.dg.plans = plans

    def get_one_info(self, p: Plan, data_type: DataType) -> Optional[Dict]:
        phase_info_lst = list(filter(lambda x: x['type'] == data_type.value, p.info_list))
        if len(phase_info_lst) == 0:
            return None
        elif len(phase_info_lst) == 1:
            return phase_info_lst[0]
        else:
            raise Exception("More than one phase info detected")

    def filter_plans(self):
        plans = self.dg.plans

        def is_phase_start(_p: Plan) -> bool:
            _info = self.get_one_info(_p, DataType.PHASE)
            if _info is not None and _info['phaseFlag'] == 'start':
                return True
            for _info in _p.info_list:
                if _info['type'] == DataType.LABEL.value \
                        and _info['label'] == 'AQE Re-optimizing':
                    return True
            return False

        new_plans = [plans[0]]
        for i in range(len(plans) - 1):
            p0 = plans[i]
            p1 = plans[i + 1]
            if p0.equals(p1):
                if i & 1 == 0:
                    # plan doesn't change by this rule
                    if p1.meta.name == 'CreateQueryStages':
                        # CreateQueryStages records 2 same plans
                        # we keep the first one
                        # here we move the info_list
                        assert new_plans[-1] == p0
                        p0.info_list += p1.info_list
                    else:
                        sys.stderr.write(f'Non-effective rule detected. {p1.meta.name}@{i}\n')
                        if len(p1.info_list) > 0:
                            print('Move info list', p1.info_list)
                            p0.info_list += p1.info_list
                        # new_plans.append(p1)
                else:
                    # between two rules
                    if is_phase_start(p1) or p1.meta.name == 'CreateQueryStages':
                        new_plans.append(p1)
                    else:
                        assert len(p1.info_list) == 0
                        # otherwise, don't add p1
                    pass
            else:
                if i & 1 == 0:
                    # normal case, plan is changed by rule
                    # if p0.phase_name != '':
                    #     new_plans.append(p0)
                    new_plans.append(p1)
                else:
                    if p1.meta.name == 'CreateQueryStages':
                        # CreateQueryStages records 2 same plans
                        # we keep the first one
                        new_plans.append(p1)
                    else:
                        # plan is changed by other reason
                        new_plans.append(p1)
                        p1.meta = SoftTransMeta()

        interval_array = []
        phase_names = []
        for i, p in enumerate(new_plans):
            if not is_phase_start(p):
                continue
            info = self.get_one_info(p, DataType.PHASE)
            if info is not None and info['phaseFlag'] == 'start':
                phase_names.append(info['phaseName'])
            else:
                phase_names.append('aqe')
            interval_array.append(i)

        ## fine-tune phase names
        # remove 2nd planning
        if phase_names.count('planning') == 2:
            index = phase_names.index('planning')
            interval_array.pop(index + 1)
            phase_names.pop(index)
        # change name
        name_dict = {
            'analysis': 'Analysis',
            'optimization': 'Optimization',
            'planning': 'Planning',
            'aqe': 'AQE'
        }
        phase_names = [name_dict[name] for name in phase_names]
        # add aqe counter
        count_idx = 0
        for i in range(len(phase_names)):
            if phase_names[i] == 'AQE':
                phase_names[i] = f'AQE#{count_idx}'
                count_idx += 1

        assert len(interval_array) > 0 and interval_array[0] == 0
        if interval_array[len(interval_array) - 1] < len(new_plans) - 1:
            interval_array.append(len(new_plans) - 1)
        else:
            phase_names.pop()

        phase_intervals = []
        for i in range(len(interval_array) - 1):
            phase_intervals.append([interval_array[i], interval_array[i + 1]])
        assert len(phase_intervals) == len(phase_names)

        self.dg.plans = new_plans
        self.dg.phase_intervals = phase_intervals
        self.dg.phase_names = phase_names

        print(phase_intervals)
        print(phase_names)

    def comp_evo_label(self):
        plans = self.dg.plans
        end_set = {interval[1] - 1 for interval in self.dg.phase_intervals}

        for i in range(len(plans) - 1):
            if i in end_set:
                # between the phase
                continue

            p0, p1 = plans[i], plans[i + 1]
            id_set0 = {v.vid for v in p0.node_dict.values()}
            id_set1 = {v.vid for v in p1.node_dict.values()}

            added_nodes = id_set1 - id_set0
            for vid in added_nodes:
                p1.node_dict[vid].evo_labels.append(EvolutionLabel.ADDED)

            to_remove_nodes = id_set0 - id_set1
            for vid in to_remove_nodes:
                p0.node_dict[vid].evo_labels.append(EvolutionLabel.TO_REMOVE)


