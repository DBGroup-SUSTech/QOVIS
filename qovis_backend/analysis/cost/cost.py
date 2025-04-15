from typing import List, Set

from common.plan import PlanNode


def edit_dist(s0: List[PlanNode], s1: List[PlanNode]) -> int:
    edit = [[i + j for j in range(len(s1) + 1)] for i in range(len(s0) + 1)]

    for i in range(1, len(s0) + 1):
        for j in range(1, len(s1) + 1):
            if s0[i - 1].vid == s1[j - 1].vid:
                d = 0
            else:
                d = 2

            edit[i][j] = min(edit[i - 1][j] + 1,
                             edit[i][j - 1] + 1,
                             edit[i - 1][j - 1] + d)

    return edit[len(s0)][len(s1)]


def label_group_cost(labels_lst: List[List[str]]) -> int:
    cost = 0
    seq_len = len(labels_lst[0])
    for i in range(seq_len):
        label_set = set([labels_lst[j][i] for j in range(len(labels_lst))])
        cost += len(label_set)
    return cost


def generate_subgraphs(struct: List[PlanNode]) -> Set[str]:
    if len(struct) == 0:
        print('empty')
        return set()

    node_set = set(struct)

    # find root
    root = struct[0]
    while len(root.consumers) != 0 and root.consumers[0] in node_set:
        root = root.consumers[0]

    # create filtered providers
    node2providers = {}
    for node in struct:
        node2providers[node] = list(filter(lambda v: v in node_set, node.providers))

    def dfs_depth(v: PlanNode) -> int:
        return max([dfs_depth(p) + 1 for p in node2providers[v]], default=0)
    max_depth = dfs_depth(root)

    def dfs_str(v: PlanNode, depth: int) -> str:
        if depth == 0:
            return '0'
        providers = node2providers[v]
        if len(providers) == 0:
            return '10'
        res = '1'
        for p in providers:
            res += dfs_str(p, depth - 1)
        return res

    subgraph_set = set()
    for cur_depth in range(max_depth + 1):
        for node in struct:
            subgraph_set.add(dfs_str(node, cur_depth))

    return subgraph_set


def compute_delta(s0: List[PlanNode], s1: List[PlanNode]):
    nodes1 = set([v.vid for v in s0])
    nodes2 = set([v.vid for v in s1])
    node_plus = nodes2 - nodes1
    node_minus = nodes1 - nodes2

    return node_plus, node_minus



