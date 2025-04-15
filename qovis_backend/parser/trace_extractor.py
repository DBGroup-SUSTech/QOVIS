import json
import os
import re
import sys
from enum import Enum
from typing import Dict, List, Optional

from entity.trace_tree import TraceNode, ProcType

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from entity.trace import Trace
from entity.plan import Plan, PlanNode, PlanEdge
from utils.id_counter import IdCounter


class RType(Enum):
    PLAN = 'plan'
    INFO = 'info'


class InfoType(Enum):
    CHILD_START = 'childStart'
    CHILD_END = 'childEnd'

    JOIN_SEL = 'joinSel'
    DY_JOIN_SEL = 'dyJoinSel'
    STRATEGY = 'strategy'
    PRUNED = 'pruned'
    STAGE_SUBMIT = 'stageSubmit'
    EFFECTIVE = 'effective'
    LABEL = 'label'


class TraceExtractor:
    def __init__(self, records: List[Dict]):
        self.records = records

        self.pid_counter = IdCounter()
        self.vid_counter = IdCounter()

        self.trace: Optional[Trace] = None

    def get(self) -> Trace:
        return self.trace

    def exec(self):
        self.clean_records()
        self.check_records()
        self.build_hierarchy()
        self.prune_ineffective()
        self.complete_plan()
        self.remove_duplicated()
        self.compress_same_proc()
        self.insert_unknown_proc()
        self.group_repeat_proc()
        self.set_plan_idx()
        self.check_trace()

    def check_records(self):
        # check if all plan records are in pairs
        record_stack = []
        pairs = []
        for r in self.records:
            if r['type'] == 'plan':
                if r['procFlag'] == 'start':
                    record_stack.append(r)
                elif r['procFlag'] == 'end':
                    if len(record_stack) == 0:
                        raise Exception("Plan record not in pairs")
                    last_r = record_stack.pop()
                    pairs.append((last_r, r))
                else:
                    raise Exception("Unknown plan record proc flag")
        assert len(record_stack) == 0, "Plan record not in pairs"

        # patch on AQE pairs
        # while len(record_stack) != 0:
        #     record = record_stack.pop()
        #     assert 'AQE' in record['name'], 'Patch can only fix AQE pairs'
        #     assert record['procFlag'] == 'start', 'Patch can only fix AQE pairs'
        #     # try to insert an end record
        #     # find next start record after this record
        #     next_start_record = None
        #     for r in self.records[self.records.index(record) + 1:]:
        #         if r['type'] == 'plan' \
        #                 and r['name'] == 'AQE'\
        #                 and r['procFlag'] == 'start':
        #             next_start_record = r
        #             break
        #     assert next_start_record is not None, 'Patch can only fix AQE pairs'
        #     idx = self.records.index(next_start_record)
        #     end_record = {
        #         'type': 'plan',
        #         'procFlag': 'end',
        #         'name': record['name'],
        #         'procType': record['procType'],
        #         'plan': next_start_record['plan'].copy(),
        #         'timestamp': next_start_record['timestamp'],
        #     }
        #     self.records.insert(idx, end_record)


        # check if all pairs are valid
        for pair in pairs:
            for attr in ['name', 'procType']:
                if pair[0][attr] != pair[1][attr]:
                    print(pair[0])
                    print(pair[1])
                    raise Exception("Plan record pairs not match")

    def clean_records(self):
        # remove all records for ResolveDeserializer

        def is_resolve_deserializer(r):
            return r['name'].endswith('Analyzer$ResolveDeserializer') \
                   and r['plan'][0]['class'] == 'org.apache.spark.sql.catalyst.plans.logical.DeserializeToObject'

        def is_clean_expressions(r):
            return r['name'].endswith('CleanExpressions')

        new_records = []
        stack = []
        met_first_aqe = False
        for r in self.records:
            # if r['type'] == 'plan' and r['name'] == 'AQE' and not met_first_aqe:
            #     continue        # skip the first AQE
            if r['type'] == 'plan' and (is_resolve_deserializer(r) or is_clean_expressions(r)):
                if r['procFlag'] == 'start':
                    stack.append(r)
                elif r['procFlag'] == 'end':
                    stack.pop()
            elif len(stack) == 0:
                new_records.append(r)
            elif r['type'] == 'plan':
                print("Warning: normal plan record detected between removed records")
                new_records.append(r)
        self.records = new_records

        for r in self.records:
            if r['type'] == 'plan':
                assert r['plan'] is not None
                r['plan'] = self.parse_plan(r['plan'])

    def parse_plan(self, raw_plan: List[Dict]) -> Plan:
        plan = Plan(self.pid_counter.get())

        # parse plan nodes

        nodes = []
        child_cnt_list = []

        # temp data
        vis2links = {}

        for r_node in raw_plan:
            vid = self.vid_counter.get()
            clazz = r_node['class']
            name = r_node['name']
            addr = r_node['addr']
            str_ = r_node['str']

            vis2links[vid] = r_node['links']

            nodes.append(PlanNode(name, clazz, vid, str_, addr, [str_]))  # todo extract attrs
            child_cnt_list.append(r_node['childNum'])

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

            link = vis2links[consumer.vid][consumer.providers.index(provider)]

            edge = PlanEdge(provider, consumer, link)
            plan.edge_dict[edge.eid] = edge

            # add cur node

            node_stack.append(provider)
            child_cnt_stack.append(child_cnt_list[i])

        return plan

    def build_hierarchy(self):
        self.trace = Trace()
        plans: List[Plan] = []
        self.trace.plans = plans
        trace_tree = self.trace.trace_tree
        root = trace_tree.root.update('Root', ProcType.Root.value)

        # extract pairs of plans and build hierarchy tree
        node_stack: List[TraceNode] = [root]
        for r in self.records:
            if r['type'] == 'plan':
                if r['procFlag'] == 'start':
                    plans.append(r['plan'])
                    # create a tree node. end plan will be updated later
                    node = TraceNode(trace_tree.get_id()).update(r['name'], r['procType'])
                    node.start_plan = plans[-1]     # r['plan']
                    node.start_time = r['timestamp']
                    node.is_partial = r['isPartial']
                    node_stack[-1].children.append(node)  # then put it into the parent node
                    node_stack.append(node)
                elif r['procFlag'] == 'end':
                    plans.append(r['plan'])
                    node = node_stack.pop()
                    node.end_plan = plans[-1]       # r['plan']
                    node.end_time = r['timestamp']
                else:
                    # never go here as we check records before
                    raise Exception("Unknown plan record proc flag")
        # set root start and end plan
        start_plan = plans[0].copy()
        start_plan.pid = self.pid_counter.get()
        root.start_plan = start_plan
        plans.insert(0, start_plan)

        end_plan = plans[-1].copy()
        end_plan.pid = self.pid_counter.get()
        root.end_plan = end_plan
        plans.append(end_plan)

        assert len(node_stack) == 1 and node_stack[0] == root, f"Trace tree build failed. {node_stack}"

        # set events for tree nodes
        node_stack = [root]
        child_cnt_stack = [0]
        for r in self.records:
            if r['type'] == 'info':
                cur_node = node_stack[-1]
                del r['type']
                cur_node.events.append(r)
            elif r['type'] == 'plan':
                if r['procFlag'] == 'start':
                    cur_node = node_stack[-1]
                    # jump to the next child
                    node_stack.append(cur_node.children[child_cnt_stack[-1]])
                    child_cnt_stack.append(0)
                elif r['procFlag'] == 'end':
                    # back to the parent
                    child_cnt_stack.pop()
                    child_cnt_stack[-1] += 1
                    node_stack.pop()
                else:
                    raise Exception("Unknown plan record proc flag")

    def prune_ineffective(self):
        plans = self.trace.plans

        def erase(parent: Optional[TraceNode], node: TraceNode):
            assert parent is not None, "Root node can not be ineffective"
            # remove this node
            parent.children.remove(node)
            node.parent = None
            # remove related plans
            assert plans.index(node.start_plan) + 1 == plans.index(node.end_plan), \
                "Ineffective node should have adjacent start and end plan"
            plans.remove(node.start_plan)
            plans.remove(node.end_plan)

        def traverse(parent: Optional[TraceNode], node: TraceNode) -> bool:
            """ Processes a ProcNode and returns whether this node should be removed """
            # find whether this node has ineffective flag in events
            is_effective = True
            for event in node.events:
                if event['infoType'] == InfoType.EFFECTIVE.value and not event['effective']:
                    is_effective = False
                    break
            if not is_effective:
                assert len(node.children) == 0, f"Ineffective node {node.name} should be a leaf node"
                return True

            # recursively process children
            # use list to avoid lazy evaluation
            to_be_removed = list(map(lambda child: traverse(node, child), node.children))
            for child, remove in list(zip(node.children, to_be_removed)):
                if remove:
                    erase(node, child)

            if len(to_be_removed) != 0 and all(to_be_removed):
                # print(f"Prune ineffective process node (all children are removed): {node.name}")
                return True

            if len(node.children) == 0 \
                    and node.type != ProcType.Rule.value \
                    and node.start_plan.equals(node.end_plan):
                # print(f"Prune ineffective process node (no children and not a rule): {node.name}")
                return True

            return False

        before_cnt = len(plans)
        traverse(None, self.trace.trace_tree.root)
        after_cnt = len(plans)
        print(f"Prune ineffective plans: {before_cnt} -> {after_cnt}")

    def remove_duplicated(self):
        """ Remove adjacent duplicated plans and update pointers in trace tree """
        plans = self.trace.plans

        # collect and check whether each plan is only referenced once by trace node
        plan_ref_cnt = {}

        def collect(node: TraceNode):
            if node.start_plan not in plan_ref_cnt:
                plan_ref_cnt[node.start_plan] = 1
            else:
                plan_ref_cnt[node.start_plan] += 1
            if node.end_plan not in plan_ref_cnt:
                plan_ref_cnt[node.end_plan] = 1
            else:
                plan_ref_cnt[node.end_plan] += 1
            for child in node.children:
                collect(child)
        collect(self.trace.trace_tree.root)
        # check
        for plan, cnt in plan_ref_cnt.items():
            assert cnt == 1, f"Plan {plan} is referenced {cnt} times"

        def process(node: TraceNode):
            if len(node.children) == 0:
                return
            # check whether node.start_plan and first child's start_plan are the same
            p0 = node.start_plan
            p1 = node.children[0].start_plan
            if p0.equals(p1):
                node.children[0].start_plan = p0
                plans.remove(p1)

            # call it recursively and check each pair of adjacent children
            for i in range(len(node.children) - 1):
                process(node.children[i])
                p0 = node.children[i].end_plan
                p1 = node.children[i + 1].start_plan
                if p0.equals(p1):
                    node.children[i + 1].start_plan = p0
                    plans.remove(p1)
            process(node.children[-1])

            # check whether node.end_plan and last child's end_plan are the same
            p0 = node.children[-1].end_plan
            p1 = node.end_plan
            if p0.equals(p1):
                node.end_plan = p0
                plans.remove(p1)

        before_cnt = len(plans)
        process(self.trace.trace_tree.root)
        after_cnt = len(plans)
        print(f"Remove duplicated plans: {before_cnt} -> {after_cnt}")

    def remove_duplicated_bk(self):
        """ Remove adjacent duplicated plans and update pointers in trace tree """
        plans = self.trace.plans

        # build link from plan to trace tree node
        pid2node: Dict[int, TraceNode] = {}

        def collect(node: TraceNode):
            start_pid = node.start_plan.pid
            assert start_pid not in pid2node, f"Duplicate start pid {start_pid}"
            pid2node[start_pid] = node

            for child in node.children:
                collect(child)

            end_pid = node.end_plan.pid
            assert end_pid not in pid2node, f"Duplicate end pid {end_pid}"
            pid2node[end_pid] = node

        collect(self.trace.trace_tree.root)

        # remove duplicated plans
        before_cnt = len(plans)
        i = 0
        while i < len(plans) - 1:
            if plans[i].equals(plans[i + 1]):
                keep_plan = plans[i]
                remove_plan = plans[i + 1]
                # update trace tree
                node0 = pid2node[keep_plan.pid]
                node1 = pid2node[remove_plan.pid]
                if node0 == node1:
                    # this process has no effect so we keep two plans
                    print(f"Warning: duplicated plans in the same process {node0}")
                else:
                    if node1.start_plan == remove_plan:
                        assert node1.end_plan != remove_plan
                        node1.start_plan = keep_plan
                    elif node1.end_plan == remove_plan:
                        node1.end_plan = keep_plan
                    plans.remove(remove_plan)
            else:
                i += 1
        after_cnt = len(plans)
        print(f"Remove duplicated plans: {before_cnt} -> {after_cnt}")

    @staticmethod
    def merge_plan(plan_with_placeholder: Plan, placeholder: PlanNode, incomplete: Plan, link: str = '') -> Plan:
        if plan_with_placeholder.root == placeholder:
            return incomplete

        # copy plan
        new_plan = plan_with_placeholder.copy()
        new_plan.pid = incomplete.pid

        # use plan_later_node in the copy
        placeholder = new_plan.node_dict[placeholder.vid]

        # clean new_plan

        assert len(placeholder.consumers) == 1
        link_node = placeholder.consumers[0]
        # cache position of original node
        idx_cache = link_node.providers.index(placeholder)

        nodes_to_remove = []

        def collect(x: PlanNode):
            nodes_to_remove.append(x)
            for y in x.providers:
                collect(y)

        collect(placeholder)

        for node_remove in nodes_to_remove:
            del new_plan.node_dict[node_remove.vid]
            # only delete cur -> consumer, as all edge can be removed
            for c in node_remove.consumers:
                del new_plan.edge_dict[PlanEdge.get_eid(node_remove, c)]

        # link target plan to new plan, replacing subtree from plan_later_node
        # target_copy_root -> link_node

        target_copy = incomplete.copy()

        # first update relation in target plan
        new_plan.node_dict.update(target_copy.node_dict)
        new_plan.edge_dict.update(target_copy.edge_dict)

        target_copy_root = target_copy.root  # is the replacement of plan_later_node

        # add edge
        link_edge = PlanEdge(target_copy_root, link_node, link)
        new_plan.edge_dict[link_edge.eid] = link_edge
        # add node dependency
        assert len(target_copy_root.consumers) == 0
        target_copy_root.consumers.append(link_node)
        link_node.providers[idx_cache] = target_copy_root
        assert link_node.providers[idx_cache] is target_copy_root

        return new_plan

    def set_plan_idx(self):
        plans = self.trace.plans

        # tree traversal
        def traverse(node: TraceNode):
            for child in node.children:
                traverse(child)
            assert node.start_plan is not None
            assert node.end_plan is not None
            node.start_idx = plans.index(node.start_plan)
            node.end_idx = plans.index(node.end_plan)

        traverse(self.trace.trace_tree.root)

    def check_trace(self):
        # check the start and end plans of each node are consistent with the children
        # besides, check the end plan of each child node is consistent with the start plan of next child

        def check_consistent_recursively(node: TraceNode):
            if len(node.children) == 0:
                return

            first_child = node.children[0]
            if node.start_idx != first_child.start_idx:
                raise Exception(f"Trace node {node} start plan {node.start_idx} is not consistent with "
                                f"the first child {first_child} start plan {first_child.start_idx}")

            # check the end plan of each child is consistent with the start plan of next child
            for i in range(len(node.children) - 1):
                child = node.children[i]
                next_child = node.children[i + 1]
                if child.end_idx != next_child.start_idx:
                    raise Exception(f"Trace node {node} end plan {child.end_idx} is not consistent with "
                                    f"the next child {next_child} start plan {next_child.start_idx}")

            last_child = node.children[-1]
            if node.end_idx != last_child.end_idx:
                raise Exception(f"Trace node {node} end plan {node.end_idx} is not consistent with "
                                f"the last child {last_child} end plan {last_child.end_idx}")

            for child in node.children:
                check_consistent_recursively(child)

        check_consistent_recursively(self.trace.trace_tree.root)

    def compress_same_proc(self):
        """ Compress process node in trace tree that only have one child with the same name """

        def traverse(node: TraceNode):
            if len(node.children) == 1 and node.name == node.children[0].name:
                assert node.start_idx == node.children[0].start_idx
                assert node.end_idx == node.children[0].end_idx
                node.children = node.children[0].children
                traverse(node)
            else:
                for child in node.children:
                    traverse(child)

        traverse(self.trace.trace_tree.root)

    def insert_unknown_proc(self):
        """ Insert unknown process node in trace tree to make it consistent """
        # the start and end plans of each node are consistent with the children
        # and the end plan of each node is the start plan of the next node
        # otherwise, insert unknown process node

        trace_tree = self.trace.trace_tree

        def insert_unknown_recursively(node: TraceNode):
            if len(node.children) == 0:
                return

            first_child = node.children[0]
            if node.start_plan != first_child.start_plan:
                unknown_node = TraceNode(trace_tree.get_id(), 'Unknown', ProcType.Unknown.value)
                unknown_node.start_plan = node.start_plan
                unknown_node.end_plan = first_child.start_plan
                node.children.insert(0, unknown_node)

            # check the end plan of each node is the start plan of the next node
            new_children = []
            for i in range(len(node.children) - 1):
                child = node.children[i]
                next_child = node.children[i + 1]
                new_children.append(child)
                if child.end_plan != next_child.start_plan:
                    unknown_node = TraceNode(trace_tree.get_id(), 'Unknown', ProcType.Unknown.value)
                    unknown_node.start_plan = child.end_plan
                    unknown_node.end_plan = next_child.start_plan
                    new_children.append(unknown_node)
            new_children.append(node.children[-1])
            node.children = new_children

            last_child = node.children[-1]
            if node.end_plan != last_child.end_plan:
                unknown_node = TraceNode(trace_tree.get_id(), 'Unknown', ProcType.Unknown.value)
                unknown_node.start_plan = last_child.end_plan
                unknown_node.end_plan = node.end_plan
                node.children.append(unknown_node)

            for child in node.children:
                insert_unknown_recursively(child)

        insert_unknown_recursively(self.trace.trace_tree.root)

    def complete_plan(self):
        # find all proc node s.t. isPartial = true

        # def find_partial_proc(node: TraceNode):
        #     if node.is_partial:
        #         return [node]
        #     res = []
        #     for child in node.children:
        #         res += find_partial_proc(child)
        #     return res
        #
        # partial_proc = find_partial_proc(self.trace.trace_tree.root)
        # print(f"Partial proc: {partial_proc}")

        # replace the head with the subquery plan for all plans in the children
        def replace_head_recursively(node: TraceNode, plan_model: Plan, head: PlanNode, link: str = ''):
            new_start_plan = self.merge_plan(plan_model, head, node.start_plan, link)
            node.start_plan.shallow_copy_from(new_start_plan)
            new_end_plan = self.merge_plan(plan_model, head, node.end_plan, link)
            node.end_plan.shallow_copy_from(new_end_plan)
            for child in node.children:
                replace_head_recursively(child, plan_model, head, link)

        def process_prepare_create_new_stages(node: TraceNode) -> bool:
            if node.name != 'Create Query Stages':
                return False

            def process_recursively(node1: TraceNode):
                if len(node1.children) == 0:
                    return

                plan_model = node1.start_plan

                for child1 in node1.children:
                    # todo change this name
                    if child1.name == 'Prepare Creating New Stage':
                        process_recursively(child1)

                    # find the head of the subquery in the plan model
                    head = plan_model.find_node(lambda x: x.addr == child1.start_plan.root.addr)
                    assert head is not None
                    assert head != plan_model.root, "This func process e.child, so it should not be root"

                    # then complete all plans in child1 using plan_model
                    replace_head_recursively(child1, plan_model, head)
                    plan_model = child1.end_plan

            process_recursively(node)
            return True

        def process_create_spark_plan(node: TraceNode) -> bool:
            if node.name != 'Create Spark Plan' and node.name != 'PlannerExec':
                return False
            while len(node.children) == 1:
                node = node.children[0]

            def is_plan_later_head(plan: Plan, plan_node: PlanNode) -> bool:
                if plan_node == plan.root:
                    return False
                if len(plan_node.consumers) != 1:
                    return False
                consumer = plan_node.consumers[0]
                edge = plan.edge_dict[PlanEdge.get_eid(plan_node, consumer)]
                return edge.link == 'PlanLater'

            plan_model = node.start_plan        # this plan don't contain plan later node
            for child in node.children:
                # find first node in the plan model which output edge is PlanLater
                head = plan_model.find_node_preorder(lambda x: is_plan_later_head(plan_model, x))
                if head is None:
                    plan_model = child.end_plan
                    continue
                # update planning strategy plans
                replace_head_recursively(child, plan_model, head)
                # update plan model
                plan_model = child.end_plan
            return True

        def process_resolve_subquery(node: TraceNode) -> bool:
            if node.name != 'org.apache.spark.sql.catalyst.analysis.Analyzer$ResolveSubquery':
                return False
            plan_model = node.start_plan
            # find the head of the subquery in the plan model
            first_child_plan = node.children[0].start_plan
            head = first_child_plan.root
            head_in_model = plan_model.find_node(lambda x: x.addr == head.addr)
            assert head_in_model is not None
            if head_in_model == plan_model.root:
                # the head is the root of the plan model, no need to replace
                return True
            # find the output edge of the head
            assert len(head_in_model.consumers) == 1
            consumer = head_in_model.consumers[0]
            edge = plan_model.edge_dict[PlanEdge.get_eid(head_in_model, consumer)]
            # complete the plans for children
            for child in node.children:
                replace_head_recursively(child, plan_model, head_in_model, edge.link)
            return True

        # traverse the trace tree and try to process corresponding plans
        def traverse(node: TraceNode):
            success = process_prepare_create_new_stages(node)
            if success:
                return
            success = process_resolve_subquery(node)
            if success:
                return
            success = process_create_spark_plan(node)
            if success:
                return
            # try to process the children
            for child in node.children:
                traverse(child)

        traverse(self.trace.trace_tree.root)

    def group_repeat_proc(self):
        """ Group the looped process nodes and create a new node """

        trace_tree = self.trace.trace_tree

        def traverse(node: TraceNode):
            if len(node.children) == 0:
                return

            if node.type != ProcType.Group.value:
                new_children = []
                i = 0
                while i < len(node.children):
                    child = node.children[i]
                    # find the next node with the same name
                    j = i + 1
                    while j < len(node.children) and node.children[j].name == child.name:
                        j += 1
                    # create a new group node if there are more than one node with the same name
                    if j - i > 1:
                        group_node = TraceNode(trace_tree.get_id(), child.name, ProcType.Group.value)
                        group_node.start_plan = child.start_plan
                        group_node.end_plan = node.children[j - 1].end_plan
                        group_node.children = node.children[i:j]
                        new_children.append(group_node)
                        i = j
                    else:
                        new_children.append(child)
                        i += 1
                node.children = new_children

            for child in node.children:
                traverse(child)

        traverse(self.trace.trace_tree.root)

