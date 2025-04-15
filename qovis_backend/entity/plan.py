from typing import Dict, Optional, List, Callable

from utils.tree_utils import to_tree_str


class Plan:
    def __init__(self, pid: int):
        self.pid = pid
        self.root: Optional[PlanNode] = None
        self.node_dict: Dict[int, PlanNode] = {}
        self.edge_dict: Dict[str, PlanEdge] = {}
        self.labels: List[str] = []

    def shallow_copy_from(self, plan: 'Plan'):
        self.pid = plan.pid
        self.root = plan.root
        self.node_dict = plan.node_dict
        self.edge_dict = plan.edge_dict
        self.labels = plan.labels

    def copy(self):
        """
        Node attributes and labels are shallow copied.
        """
        plan = Plan(self.pid)
        plan.labels = self.labels.copy()

        # nodes
        for v in self.node_dict.values():
            plan.node_dict[v.vid] = PlanNode(v.name, v.clazz, v.vid, v.str_, v.addr, v.attrs)

        # edges
        for e in self.edge_dict.values():
            p = plan.node_dict[e.provider.vid]
            c = plan.node_dict[e.consumer.vid]
            p.consumers.append(c)
            c.providers.append(p)
            plan.edge_dict[e.eid] = PlanEdge(p, c, e.link)

        for v in self.node_dict.values():
            node = plan.node_dict[v.vid]
            node.providers = [plan.node_dict[p.vid] for p in v.providers]
            node.consumers = [plan.node_dict[c.vid] for c in v.consumers]

        # root
        plan.root = plan.node_dict[self.root.vid]

        plan.labels = self.labels.copy()

        return plan

    def __repr__(self):
        return f"Plan#{self.pid}"

    def equals(self, other: 'Plan'):
        if not isinstance(other, Plan):
            return False
        if len(self.node_dict) != len(other.node_dict):
            return False

        def is_same(node0: PlanNode, node1: PlanNode) -> bool:
            if not node0.fast_equals(node1):
                return False
            if len(node0.providers) != len(node1.providers):
                return False
            for u, v in zip(node0.providers, node1.providers):
                if not is_same(u, v):
                    return False
            return True

        return is_same(self.root, other.root)

    def find_node(self, f: Callable[['PlanNode'], bool]) -> Optional['PlanNode']:
        for v in self.node_dict.values():
            if f(v):
                return v
        return None

    def find_node_preorder(self, f: Callable[['PlanNode'], bool]) -> Optional['PlanNode']:
        def find(node: PlanNode) -> Optional[PlanNode]:
            if f(node):
                return node
            for c in node.providers:
                found = find(c)
                if found:
                    return found
            return None
        return find(self.root)

    def dump(self) -> Dict:
        nodes = []
        for v in self.node_dict.values():
            nodes.append(v.dump())
        edges = []
        for e in self.edge_dict.values():
            edges.append(e.dump())
        return {
            'pid': self.pid,
            'root': self.root.vid,
            'nodes': nodes,
            'edges': edges,
            'labels': self.labels,
        }

    @staticmethod
    def load(dct: Dict):
        plan = Plan(dct['pid'])

        for v in dct['nodes']:
            node = PlanNode(v['name'], v['clazz'], v['vid'], v['str'], v['addr'], v['attrs'])
            plan.node_dict[node.vid] = node

        for e in dct['edges']:
            p = plan.node_dict[e['pVid']]
            c = plan.node_dict[e['cVid']]
            edge = PlanEdge(p, c, e['link'])
            plan.edge_dict[edge.eid] = edge

        for v in dct['nodes']:
            node = plan.node_dict[v['vid']]
            node.providers = [plan.node_dict[vid] for vid in v['pros']]
            node.consumers = [plan.node_dict[vid] for vid in v['cons']]

        plan.root = plan.node_dict[dct['root']]

        plan.labels = dct['labels']

        return plan

    def to_tree_str(self):
        return f'{str(self)}\n' + self.root.to_tree_str()


class PlanNode:
    def __init__(self, name: str, clazz: str, vid: int, str_: str, addr: int, attrs: List[str]):
        self.providers: List[PlanNode] = []
        self.consumers: List[PlanNode] = []

        self.name: str = name
        self.clazz: str = clazz
        self.vid: int = vid
        self.str_: str = str_
        self.addr: int = addr
        self.attrs: List[str] = attrs

    def __repr__(self):
        return f"{self.name}#{self.vid}"

    def fast_equals(self, other: 'PlanNode'):
        if not isinstance(other, PlanNode):
            return False
        return self.addr == other.addr

    def dump(self):
        return {
            'vid': self.vid,
            'name': self.name,
            'clazz': self.clazz,
            'str': self.str_,
            'addr': self.addr,
            'attrs': self.attrs,
            'pros': [p.vid for p in self.providers],
            'cons': [c.vid for c in self.consumers],
        }

    def to_tree_str(self):
        return to_tree_str(self, lambda v: v.providers, lambda v: str(v))


class PlanEdge:
    def __init__(self, provider: PlanNode, consumer: PlanNode, link: str):
        self.eid = self.get_eid(provider, consumer)
        self.provider = provider
        self.consumer = consumer
        self.link: str = link

    @staticmethod
    def get_eid(provider: PlanNode, consumer: PlanNode):
        return f'{provider.vid}-{consumer.vid}'

    def __repr__(self):
        return f'{str(self.provider)}->{str(self.consumer)}'

    def dump(self):
        return {
            'pVid': self.provider.vid,
            'cVid': self.consumer.vid,
            'link': self.link,
        }
