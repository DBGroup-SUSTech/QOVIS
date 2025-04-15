from typing import List, Dict, Union

from common.graph import Meta, Graph, Node


class PlanMeta(Meta):
    node_id = 0
    node_id_dict: Dict[str, int] = {}   # addr -> id

    def __init__(self, meta_id: int):
        super().__init__(meta_id, 'plan')
        self.plan = None

    def to_dict(self):
        result = super().to_dict()
        result.update({
            "plan": self.plan,
        })
        return result

    @staticmethod
    def reset_node_id():
        PlanMeta.node_id = 0
        PlanMeta.node_id_dict = {}

    @staticmethod
    def fast_equal(plan0, plan1):
        if plan0 is None or plan1 is None:
            return False
        if len(plan0) != len(plan1):
            return False
        for i in range(len(plan0)):
            if plan0[i]['id'] != plan1[i]['id']:
                return False
        return True

    @staticmethod
    def clean_plan(plan: List[Dict]) -> List[Dict]:
        new_plan = []
        fields = ['node-name', 'str', 'num-children', 'addr']
        new_fields = ['name', 'str', 'childCnt', 'id']
        for node in plan:
            new_node = {}
            for f, n_f in zip(fields, new_fields):
                new_node[n_f] = node[f]
            # update id
            if new_node['id'] in PlanMeta.node_id_dict:
                new_node['id'] = PlanMeta.node_id_dict[new_node['id']]
            else:
                # addr -> id
                PlanMeta.node_id_dict[new_node['id']] = PlanMeta.node_id
                new_node['id'] = PlanMeta.node_id
                PlanMeta.node_id += 1
            new_plan.append(new_node)
        return new_plan


class RuleMeta(Meta):
    def __init__(self, meta_id: int):
        super().__init__(meta_id, 'rule')
        self.type = None
        self.name = None
        self.effective = True
        self.run_time = 0
        self.class_name = ""

        self.batch_name: str = ""
        self.batch_id: int = -1

    def to_dict(self):
        result = super().to_dict()
        result.update({
            "type": self.type,
            "name": self.name,
            "effective": self.effective,
            "runTime": self.run_time,
            "className": self.class_name,
            "batchName": self.batch_name,
            "batchId": self.batch_id,
        })
        return result


class StrategyMeta(Meta):
    def __init__(self, meta_id: int):
        super().__init__(meta_id, 'strategy')
        self.type = None
        self.name = None
        self.effective = True
        self.run_time = 0
        self.class_name = ""

        self.invoke_cnt: int = -1
        self.rid: int = -1

    def to_dict(self):
        result = super().to_dict()
        result.update({
            "type": self.type,
            "name": self.name,
            "effective": self.effective,
            "runTime": self.run_time,
            "className": self.class_name,
            "invokeCnt": self.invoke_cnt,
            "rid": self.rid,
        })
        return result


class SoftTransMeta(Meta):
    def __init__(self, meta_id: int):
        super().__init__(meta_id, 'soft_trans')

    def to_dict(self):
        return super().to_dict()


class TGraph(Graph):
    def __init__(self):
        super().__init__()
        self._meta_id_cnt = 0

    def _get_meta_id(self) -> int:
        ret = self._meta_id_cnt
        self._meta_id_cnt += 1
        return ret

    def build_from_raw_trace(self, records: List[Dict]):
        self._clean_plan(records)

        # extract block first
        # in each block, one plan in, one plan out

        dividers = []
        # indicates the pos after records[i]
        for possible_div in range(1, len(records)):
            p = records[possible_div - 1]
            q = records[possible_div]
            if p['rType'] != q['rType']:
                dividers.append(possible_div)

        blocks = []
        dividers = [0] + dividers + [len(records)]
        for i in range(len(dividers) - 1):
            start = dividers[i]
            end = dividers[i + 1]
            blocks.append(records[start: end])

        # create the dag structure

        assert blocks[0][0]['rType'] == 'rule'

        last_node: Union[Node[PlanMeta], None] = None        # the last node in previous block/record
        for block in blocks:
            if block[0]['rType'] == 'rule':
                # is a rule executor block
                last_node = self._process_rule_block(block, last_node)

            elif block[0]['rType'] == 'strategy':
                # is a strategy planner block
                assert last_node is not None
                invoke_groups = {}
                for record in block:
                    if record['invokeCnt'] in invoke_groups:
                        invoke_groups[record['invokeCnt']].append(record)
                    else:
                        invoke_groups[record['invokeCnt']] = [record]
                sorted_items = list(invoke_groups.items())
                sorted_items.sort(key=lambda x: x[0])
                for _, b in sorted_items:
                    last_node = self._process_strategy_block(b, last_node)

            else:
                raise "Unknown record type " + block[0]['rType']

    def _process_rule_block(self, block: List[Dict], last_node: Node[PlanMeta]):
        for record, idx in zip(block, range(len(block))):
            # compute src node
            if last_node is not None:
                if PlanMeta.fast_equal(last_node.plan, record['oldPlan']):
                    # use last_node as src
                    src = last_node
                else:
                    # build src node and connect it to last_node
                    src = self.add_node(PlanMeta(self._get_meta_id()))
                    src.plan = record['oldPlan']
                    self.add_edge(last_node, src, SoftTransMeta(self._get_meta_id()))
            else:
                # just build the src node, as last_node is None
                src = self.add_node(PlanMeta(self._get_meta_id()))
                src.plan = record['oldPlan']

            # now all the rules are effective

            dst = self.add_node(PlanMeta(self._get_meta_id()))
            dst.plan = record['newPlan']

            rule_edge = self.add_edge(src, dst, RuleMeta(self._get_meta_id()))
            rule_edge.type = record['type']
            rule_edge.name = record['ruleName']
            rule_edge.effective = True
            rule_edge.run_time = record['runTime']
            rule_edge.class_name = record['className']
            rule_edge.batch_name = record['batchName']
            rule_edge.batch_id = record['batchId']

            last_node = dst
        return last_node

    def _process_strategy_block(self, block: List[Dict], last_node: Node[PlanMeta]):
        rid_to_records: Dict[int, List[Dict]] = {}
        for record in block:
            if record['rid'] in rid_to_records:
                rid_to_records[record['rid']].append(record)
            else:
                rid_to_records[record['rid']] = [record]

        def build_recursively(cur_rid: int) -> Node[PlanMeta]:
            records = rid_to_records[cur_rid]

            src = self.add_node(PlanMeta(self._get_meta_id()))
            src.plan = records[0]['logicalPlan']

            for rec in records:
                strategy_meta = StrategyMeta(self._get_meta_id())
                strategy_meta.type = rec['type']
                strategy_meta.name = rec['strategyName']
                strategy_meta.effective = True
                strategy_meta.run_time = rec['runTime']
                strategy_meta.class_name = rec['className']

                strategy_meta.invoke_cnt = rec['invokeCnt']
                strategy_meta.rid = cur_rid

                for child_rid, output_plan in zip(rec['childRidSeq'], rec['physicalPlans']):
                    dst = self.add_node(PlanMeta(self._get_meta_id()))
                    dst.plan = output_plan
                    self.add_edge(src, dst, strategy_meta)

                    if child_rid in rid_to_records:
                        # still has placeholders, add a soft trans
                        # because sub process is applying on the subquery, not the original one
                        sub_plan_node = build_recursively(child_rid)
                        self.add_edge(dst, sub_plan_node, SoftTransMeta(self._get_meta_id()))
            return src

        root = build_recursively(0)  # rid starts from 0

        if PlanMeta.fast_equal(root.plan, last_node.plan):
            # replace root by last_node
            for e in root.out_edges:
                self.add_edge(last_node, e.dst, e.meta)
            self.delete_node(root.nid)
        else:
            # build connection between them
            self.add_edge(last_node, root, SoftTransMeta(self._get_meta_id()))
            last_node = root

        # spark only peek the first plan
        while len(last_node.out_edges) != 0:
            last_node = last_node.out_edges[0].dst

        return last_node

    def _clean_plan(self, records: List[Dict]):
        PlanMeta.reset_node_id()
        for r in records:
            for f in ['newPlan', 'oldPlan', 'logicalPlan']:
                if f in r:
                    r[f] = PlanMeta.clean_plan(r[f])
            for f in ['physicalPlans']:
                if f in r:
                    r[f] = [PlanMeta.clean_plan(p) for p in r[f]]


