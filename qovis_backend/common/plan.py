from enum import Enum
from typing import Dict, Optional, List


class EvolutionLabel(Enum):
    ADDED = 'added'
    TO_REMOVE = 'to_remove'


class Meta:
    def __init__(self, meta_type: str):
        self.meta_type = meta_type

    def get_labels(self):
        return []

    def dump(self) -> Dict:
        return {
            'metaType': self.meta_type,
        }

    @staticmethod
    def load(dct: Dict):
        if dct['metaType'] == 'rule':
            obj = RuleMeta.load(dct)
        elif dct['metaType'] == 'strategy':
            obj = StrategyMeta.load(dct)
        elif dct['metaType'] == 'softTrans':
            obj = SoftTransMeta.load(dct)
        elif dct['metaType'] == 'action':
            obj = ActionMeta.load(dct)
        else:
            raise Exception('Unknown meta type: ' + dct['metaType'])
        return obj


class RuleMeta(Meta):
    fields = ['type', 'name', 'effective', 'runTime', 'className', 'batchName', 'batchId']
    attrs = ['type', 'name', 'effective', 'run_time', 'class_name', 'batch_name', 'batch_id']

    def __init__(self):
        super().__init__('rule')
        self.type = None
        self.name = None
        self.effective = True
        self.run_time = 0
        self.class_name = ""

        self.batch_name: str = ""
        self.batch_id: int = -1

    def get_labels(self):
        return [self.type, self.batch_name, self.class_name]

    def __repr__(self):
        return f"RuleMeta({self.name})"

    def dump(self) -> Dict:
        result = super().dump()
        for field, attr in zip(self.fields, self.attrs):
            result[field] = getattr(self, attr)
        return result

    @staticmethod
    def load(dct: Dict):
        ret = RuleMeta()
        for field, attr in zip(RuleMeta.fields, RuleMeta.attrs):
            setattr(ret, attr, dct[field])
        return ret


class StrategyMeta(Meta):
    fields = ['type', 'name', 'effective', 'runTime', 'className', 'invokeCnt', 'rid']
    attrs = ['type', 'name', 'effective', 'run_time', 'class_name', 'invoke_cnt', 'rid']

    def __init__(self):
        super().__init__('strategy')
        self.type = None
        self.name = None
        self.effective = True
        self.run_time = 0
        self.class_name = ""

        self.invoke_cnt: int = -1
        self.rid: int = -1

    def get_labels(self):
        return [self.type, f'Planning{self.invoke_cnt}', self.class_name]

    def __repr__(self):
        return f"StrategyMeta({self.name})"

    def dump(self) -> Dict:
        result = super().dump()
        for field, attr in zip(self.fields, self.attrs):
            result[field] = getattr(self, attr)
        return result

    @staticmethod
    def load(dct: Dict):
        ret = StrategyMeta()
        for field, attr in zip(StrategyMeta.fields, StrategyMeta.attrs):
            setattr(ret, attr, dct[field])
        return ret

class ActionMeta(Meta):
    fields = ['type', 'name', 'effective', 'runTime', 'className', 'batchName', 'batchId']
    attrs = ['type', 'name', 'effective', 'run_time', 'class_name', 'batch_name', 'batch_id']

    def __init__(self):
        super().__init__('action')
        self.type = None
        self.name = None
        self.effective = True
        self.run_time = 0
        self.class_name = ""

        self.batch_name: str = ""
        self.batch_id: int = -1

    def get_labels(self):
        return [self.batch_name, self.name]

    def __repr__(self):
        return f"ActionMeta({self.name})"

    def dump(self) -> Dict:
        result = super().dump()
        for field, attr in zip(self.fields, self.attrs):
            result[field] = getattr(self, attr)
        return result

    @staticmethod
    def load(dct: Dict):
        ret = ActionMeta()
        for field, attr in zip(ActionMeta.fields, ActionMeta.attrs):
            setattr(ret, attr, dct[field])
        return ret


class SoftTransMeta(Meta):
    fields = ['type', 'name']
    attrs = ['type', 'name']

    def __init__(self):
        super().__init__('softTrans')
        self.type = 'soft trans'
        self.name = ''

    def get_labels(self):
        return [self.type, self.type, self.type]

    def __repr__(self):
        return f"SoftTransMeta({self.name})"

    def dump(self) -> Dict:
        result = super().dump()
        for field, attr in zip(self.fields, self.attrs):
            result[field] = getattr(self, attr)
        return result

    @staticmethod
    def load(dct: Dict):
        ret = SoftTransMeta()
        for field, attr in zip(SoftTransMeta.fields, SoftTransMeta.attrs):
            setattr(ret, attr, dct[field])
        return ret


class Plan:
    """
    @deprecated
    """
    def __init__(self, pid: int):
        self.pid = pid
        self.meta: Optional[Meta] = None
        self.root: Optional[PlanNode] = None
        self.node_dict: Dict[int, PlanNode] = {}
        self.edge_dict: Dict[str, PlanEdge] = {}
        self.info_list: List[Dict] = []

    def copy(self):
        """
        Meta and InfoList will use shadow copy
        """
        plan = Plan(self.pid)
        plan.meta = self.meta
        plan.info_list = self.info_list

        # nodes
        for v in self.node_dict.values():
            plan.node_dict[v.vid] = PlanNode(v.name, v.vid, v.str_, v.addr, v.plan_later)

        # edges
        for e in self.edge_dict.values():
            p = plan.node_dict[e.provider.vid]
            c = plan.node_dict[e.consumer.vid]
            p.consumers.append(c)
            c.providers.append(p)
            plan.edge_dict[e.eid] = PlanEdge(p, c)

        for v in self.node_dict.values():
            node = plan.node_dict[v.vid]
            node.providers = [plan.node_dict[p.vid] for p in v.providers]
            node.consumers = [plan.node_dict[c.vid] for c in v.consumers]

        # roots
        plan.root = plan.node_dict[self.root.vid]

        return plan

    def contain_plan_later(self) -> bool:
        return any([node.plan_later is not None for node in self.node_dict.values()])

    def __repr__(self):
        return f"Plan#{self.pid}"

    def equals(self, other: 'Plan'):
        if not isinstance(other, Plan):
            return False
        if len(self.node_dict) != len(other.node_dict):
            return False

        def is_same(node0: PlanNode, node1: PlanNode) -> bool:
            if node0.vid != node1.vid:
                return False
            if len(node0.providers) != len(node1.providers):
                return False
            for u, v in zip(node0.providers, node1.providers):
                if not is_same(u, v):
                    return False
            return True

        return is_same(self.root, other.root)

    def dump(self) -> Dict:
        nodes = []
        for v in self.node_dict.values():
            nodes.append({
                'vid': v.vid,
                'name': v.name,
                'str': v.str_,
                'addr': v.addr,
                'planLater': v.plan_later,
                'pros': [p.vid for p in v.providers],
                'cons': [c.vid for c in v.consumers],
                'evoLabels': [label.value for label in v.evo_labels]
            })
        edges = []
        for e in self.edge_dict.values():
            edges.append({
                'pVid': e.provider.vid,
                'cVid': e.consumer.vid,
            })
        info_list = []
        for info in self.info_list:
            tmp = {}
            for k, v in info.items():
                if k in ['plan', 'logicalPlan', 'physicalPlan']:
                    # print(k)
                    tmp[k] = v.dump()
                elif k in ['stages']:
                    tmp[k] = [w.dump() for w in v]
                else:
                    tmp[k] = v
            info_list.append(tmp)
        return {
            'pid': self.pid,
            'meta': self.meta.dump() if self.meta is not None else None,
            'root': self.root.vid,
            'nodes': nodes,
            'edges': edges,
            'infoList': info_list,
        }

    @staticmethod
    def load(dct: Dict):
        plan = Plan(dct['pid'])
        plan.meta = Meta.load(dct['meta']) if dct['meta'] else None

        for v in dct['nodes']:
            node = PlanNode(v['name'], v['vid'], v['str'], v['addr'], v['planLater'])
            node.evo_labels = [EvolutionLabel[label] for label in dct['evoLabels']]
            plan.node_dict[node.vid] = node

        for e in dct['edges']:
            p = plan.node_dict[e['pVid']]
            c = plan.node_dict[e['cVid']]
            edge = PlanEdge(p, c)
            plan.edge_dict[edge.eid] = edge

        for v in dct['nodes']:
            node = plan.node_dict[v['vid']]
            node.providers = [plan.node_dict[vid] for vid in v['pros']]
            node.consumers = [plan.node_dict[vid] for vid in v['cons']]

        plan.root = plan.node_dict[dct['root']]

        info_list = []
        for info in dct['infoList']:
            tmp = {}
            for k, v in info.items():
                if k in ['plan', 'logicalPlan', 'physicalPlan']:
                    tmp[k] = Plan.load(v)
                elif k in ['stages']:
                    tmp[k] = [Plan.load(w) for w in v]
                else:
                    tmp[k] = v
            info_list.append(tmp)
        plan.info_list = info_list

        return plan


class PlanNode:
    def __init__(self, name: str, vid: int, str_: str, addr: int, plan_later: Optional[int] = None):
        self.providers: List[PlanNode] = []
        self.consumers: List[PlanNode] = []

        self.name: str = name
        self.vid: int = vid
        self.str_: str = str_
        self.addr: int = addr
        self.plan_later: Optional[int] = plan_later
        self.evo_labels: List[EvolutionLabel] = []

    def __repr__(self):
        mark = "'" if self.plan_later is not None else ''
        return f"{self.name}#{self.vid}{mark}"


class PlanEdge:
    def __init__(self, provider: PlanNode, consumer: PlanNode):
        self.eid = self.get_eid(provider, consumer)
        self.provider = provider
        self.consumer = consumer

    @staticmethod
    def get_eid(provider: PlanNode, consumer: PlanNode):
        return f'{provider.vid}-{consumer.vid}'

    def __repr__(self):
        return f'{str(self.provider)}->{str(self.consumer)}'

