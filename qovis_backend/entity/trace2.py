from functools import reduce
from typing import List

from entity.trace_tree import TraceTree, TraceNode
from trans.plan.query_plan import QueryPlan
from trans.rule.trans_link import TransLink
from trans.rule.trans_path import TransPath


class Trace2:
    def __init__(self):
        self.name: str = ''
        self.plans: List[QueryPlan] = []
        self.transforms: List[TransPath] = []
        self.trace_tree: TraceTree = TraceTree()
        self.costs: list[tuple[float, float]] = []
        self.linkage_map: dict[int, List[TransLink]] = {}

    def build_linkages(self):
        # for each leaf node, there exists a transform path object

        leaf_id_to_paths: dict[int, TransPath] = {}
        linkage_map: dict[int, List[TransLink]] = {}

        def link_path_objects(node: TraceNode):
            if not node.children:
                # is a leaf
                assert node.start_idx == node.end_idx - 1
                path = self.transforms[node.start_idx]
                leaf_id_to_paths[node.id] = path
                return
            for c in node.children:
                link_path_objects(c)

        def process_links(node: TraceNode):
            if not node.children:
                # is a leaf
                path = leaf_id_to_paths[node.id]
                linkage_map[node.id] = path.get_links()
                return

            for c in node.children:
                process_links(c)

            # merge linkages
            links_list: list[list[TransLink]] = [linkage_map[c.id] for c in node.children]
            links = reduce(lambda x, y: TransPath.merge_links(x, y), links_list)
            # unique links
            unique_links = []
            for link in links:
                if link not in unique_links:
                    unique_links.append(link)
            linkage_map[node.id] = unique_links

        link_path_objects(self.trace_tree.root)
        process_links(self.trace_tree.root)
        self.linkage_map = linkage_map

    def dump(self):
        return {
            'name': self.name,
            'plans': [p.dump() for p in self.plans],
            'trans': [t.dump() for t in self.transforms],
            'tree': self.trace_tree.dump(),
            'costs': self.costs,
            'linksMap': {id: [link.dump() for link in links] for id, links in self.linkage_map.items()},
        }

    @staticmethod
    def load(obj):
        raise NotImplementedError
