from typing import List, Dict

from common.plan import PlanNode
from utils.id_counter import IdCounter


class SNode:
    def __init__(self, vid: int):
        self.vid: int = vid
        self.in_edges: List[SEdge] = []
        self.out_edges: List[SEdge] = []
        self.type: str = 'unknown'
        self.structure_seq: List[List[PlanNode]] = []
        self.eff_lst: [bool] = []


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
        self.seq_cnt = 0

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

    def dump(self) -> Dict:
        nodes = []
        for v in self.node_dict.values():
            nodes.append({
                'vid': v.vid,
                'type': v.type,
                'structureSeq': [[pn.vid for pn in s] for s in v.structure_seq],
                'effList': v.eff_lst,
            })
        edges = []
        for e in self.edge_dict.values():
            edges.append({
                'src': e.src.vid,
                'dst': e.dst.vid,
            })
        return {
            'seqCnt': self.seq_cnt,
            'nodes': nodes,
            'edges': edges,
        }

