from typing import TypeVar, Generic, List, Dict


class Meta:
    def __init__(self, meta_id: int, meta_type: str):
        self.meta_id = meta_id
        self.meta_type = meta_type

    def to_dict(self):
        return {
            'metaId': self.meta_id,
            'metaType': self.meta_type,
        }

    # def merge_to(self, dct: Dict) -> None:
    #     self_dict = self.to_dict()
    #
    #     self_set, other_set = set(self_dict), set(dct)
    #     diff = self_set.intersection(other_set)
    #     if len(diff) != 0:
    #         print(f'Duplicated key found when merging meta:', list(diff))
    #
    #     dct.update(self_dict)


T = TypeVar('T', bound=Meta)


class Node(Generic[T]):
    def __init__(self, nid: int, meta: T):
        self.nid: int = nid
        self.meta: T = meta
        self.in_edges: List[Edge] = []
        self.out_edges: List[Edge] = []

    def __getattr__(self, item):
        return getattr(self.meta, item)

    def __setattr__(self, key, value):
        if key in ['nid', 'meta', 'in_edges', 'out_edges']:
            self.__dict__[key] = value
        else:
            getattr(self.meta, key)  # will raise an error if it doesn't exist
            setattr(self.meta, key, value)

    def to_dict(self):
        result = {
            "nid": self.nid,
            "inEdges": [e.eid for e in self.in_edges],
            "outEdges": [e.eid for e in self.out_edges],
            "meta": self.meta.to_dict(),
        }
        return result


class Edge(Generic[T]):
    def __init__(self, src: Node, dst: Node, meta: T):
        super().__init__()
        self.eid: str = Edge.get_id(src, dst)
        self.src: Node = src
        self.dst: Node = dst
        self.meta: T = meta

    @staticmethod
    def get_id(src: Node, dst: Node) -> str:
        return f'{src.nid}-{dst.nid}'

    def __getattr__(self, item):
        return self.meta[item]

    def __setattr__(self, key, value):
        if key in ['eid', 'src', 'dst', 'meta']:
            self.__dict__[key] = value
        else:
            getattr(self.meta, key)     # will raise an error if it doesn't exist
            setattr(self.meta, key, value)

    def to_dict(self):
        result = {
            "eid": self.eid,
            "src": self.src.nid,
            "dst": self.dst.nid,
            "meta": self.meta.to_dict(),
        }
        return result


class Graph:
    def __init__(self):
        self.node_dict: Dict[int, Node] = {}
        self.edge_dict: Dict[str, Edge] = {}
        self._id_cnt: int = 0

    def add_node(self, meta: T) -> Node[T]:
        node = Node(self._id_cnt, meta)
        self.node_dict[node.nid] = node
        self._id_cnt += 1
        return node

    def delete_node(self, nid: int):
        node = self.node_dict[nid]
        for e in node.in_edges + node.out_edges:
            self.delete_edge(e.eid)
        del self.node_dict[nid]

    def add_edge(self, src: Node, dst: Node, meta: T) -> Edge[T]:
        edge = Edge(src, dst, meta)
        src.out_edges.append(edge)
        dst.in_edges.append(edge)
        self.edge_dict[edge.eid] = edge
        return edge

    def delete_edge(self, eid: str):
        edge = self.edge_dict[eid]
        edge.src.out_edges.remove(edge)
        edge.dst.in_edges.remove(edge)
        del self.edge_dict[eid]

    def nodes(self) -> List[Node]:
        return list(self.node_dict.values())

    def edges(self) -> List[Edge]:
        return list(self.edge_dict.values())

    def to_dict(self) -> Dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes()],
            "edges": [e.to_dict() for e in self.edges()],
        }


if __name__ == '__main__':
    node = Node(0, Meta(0, 'test_meta'))
    print(node.meta_id)
    print(node.meta_type)
    node.meta_id = 1
    node.meta_type = 'x'
    print(node.meta_id)
    print(node.meta_type)

    print('bar', node.bar)  # an error
    node.foo = 1  # an error
