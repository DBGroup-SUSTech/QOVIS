from typing import Dict


class Plan:
    def __init__(self):
        self.plan_id = None
        self.root = None
        self.node_dict: Dict[int, PlanNode] = {}
        self.edge_dict: Dict[str, PlanEdge] = {}

    def init_from(self, raw_plan):
        self.plan_id = raw_plan['nid']
        raw_nodes = raw_plan['meta']['plan']
        nodes = [PlanNode(n['name'], n['id'], n['str']) for n in raw_nodes]
        child_cnt_dict = {n['id']: n['childCnt'] for n in raw_nodes}

        # init root

        self.root = nodes[0]
        node_stack = [self.root]
        for node in nodes[1:]:
            while child_cnt_dict[node_stack[-1].id] == 0:
                node_stack.pop()
            parent = node_stack[-1]
            node.parent = parent
            parent.children.append(node)

            child_cnt_dict[parent.id] -= 1
            node_stack.append(node)

        # init dict

        self.node_dict = {n.id: n for n in nodes}
        for node in nodes:
            for child in node.children:
                edge = PlanEdge(node, child)
                self.edge_dict[edge.id] = edge

        return self


class PlanNode:
    def __init__(self, name, id, str_):
        self.parent = None
        self.children = []

        self.name = name
        self.id = id
        self.str_ = str_


class PlanEdge:
    def __init__(self, parent, child):
        self.id = f'{parent.id}-{child.id}'
        self.parent = parent.id
        self.child = child

