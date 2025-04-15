from typing import List, Dict, Optional

from common.plan import Plan, PlanNode
from utils.id_counter import IdCounter


class SNode:
    def __init__(self, vid: int):
        self.vid: int = vid
        self.in_edges: List[SEdge] = []
        self.out_edges: List[SEdge] = []
        self.plan_nodes: List[PlanNode] = []


class SEdge:
    def __init__(self, src: SNode, dst: SNode):
        super().__init__()
        self.eid: str = SEdge.get_id(src, dst)
        self.src: SNode = src
        self.dst: SNode = dst

    @staticmethod
    def get_id(src: SNode, dst: SNode) -> str:
        return f'{src.vid}-{dst.vid}'


class SGraph:
    def __init__(self):
        self.vid_counter: IdCounter = IdCounter()
        self.node_dict: Dict[int, SNode] = {}
        self.edge_dict: Dict[str, SEdge] = {}
        self.plan: Plan = None

    def add_node(self) -> SNode:
        node = SNode(self.vid_counter.get())
        self.node_dict[node.vid] = node
        return node

    def delete_node(self, vid: int) -> SNode:
        node = self.node_dict[vid]
        for e in node.in_edges + node.out_edges:
            self.delete_edge(e.eid)
        del self.node_dict[vid]
        return node

    def add_edge(self, src: SNode, dst: SNode) -> SEdge:
        edge = SEdge(src, dst)
        src.out_edges.append(edge)
        dst.in_edges.append(edge)
        self.edge_dict[edge.eid] = edge
        return edge

    def delete_edge(self, eid: str) -> SEdge:
        edge = self.edge_dict[eid]
        edge.src.out_edges.remove(edge)
        edge.dst.in_edges.remove(edge)
        del self.edge_dict[eid]
        return edge

    def nodes(self) -> List[SNode]:
        return list(self.node_dict.values())

    def edges(self) -> List[SEdge]:
        return list(self.edge_dict.values())

    @classmethod
    def load_from_plan(cls, p: Plan):
        sg = SGraph()
        p_vid_to_s_vid = {}
        for v in p.node_dict.values():
            sv = sg.add_node()
            sv.plan_nodes.append(v)
            p_vid_to_s_vid[v.vid] = sv.vid
        for e in p.edge_dict.values():
            s0 = sg.node_dict[p_vid_to_s_vid[e.provider.vid]]
            s1 = sg.node_dict[p_vid_to_s_vid[e.consumer.vid]]
            sg.add_edge(s0, s1)
        sg.plan = p
        return sg

    def dump(self) -> Dict:
        nodes = []
        for v in self.node_dict.values():
            nodes.append({
                'vid': v.vid,
                'planNodes': [pv.vid if pv else None for pv in v.plan_nodes],
            })
        edges = []
        for e in self.edge_dict.values():
            edges.append({
                'src': e.src.vid,
                'dst': e.dst.vid,
            })
        return {
            'plan': self.plan.dump(),
            'nodes': nodes,
            'edges': edges,
        }

