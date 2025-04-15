from typing import List, Optional, Set

from entity.plan import PlanNode, Plan
from entity.transform import Transform


class TreeAlignAlgo:
    def __init__(self, plan1, plan2):
        self.plan1: Plan = plan1
        self.plan2: Plan = plan2

        # indices start from 1
        self.nodes1: List[PlanNode] = self.get_subtree_nodes(self.plan1.root)
        self.nodes1.insert(0, None)
        self.nodes2: List[PlanNode] = self.get_subtree_nodes(self.plan2.root)
        self.nodes2.insert(0, None)

        # index in nodes1, index in nodes2
        # each item is a float for D(T1[i], T2[j])
        # the indices start from 1
        # the first row and column are for empty tree
        self.tree_mem: List[List[float]] = []
        self.init_tree_mem()

        # index in nodes1, index in nodes2,
        # start index s in the children of nodes1[i], start index t in the children of nodes2[i]
        # each item is a matrix for {D(F1[i_s, i_p], F2[j_t, j_q]) | s <= p <= deg(node1[i]), t <= q <= deg(node2[j])}
        # the indices of the matrix start from 1
        self.forest_mem: List[List[List[List[List[List[float]]]]]] = []
        self.init_forest_mem()

        # sort by index in nodes1
        # each item is a float for D(T1[i], empty)
        # the indices start from 1
        self.forest1_to_emtpy: List[float] = [None for _ in range(len(self.nodes1))]

        # sort by index in nodes2
        # each item is a float for D(empty, T2[j])
        # the indices start from 1
        self.empty_to_forest2: List[float] = [None for _ in range(len(self.nodes2))]

        self.min_cost: Optional[float] = None
        self.transforms: Optional[Set[Transform]] = None

    def init_tree_mem(self):
        for i in range(len(self.nodes1) + 1):
            self.tree_mem.append([])
            for j in range(len(self.nodes2) + 1):
                self.tree_mem[i].append(None)

    def get_tree_mem(self, i: int, j: int) -> float:
        """
        Notice that the indices start from 1
        """
        res = self.tree_mem[i][j]
        assert res is not None
        return res

    def set_tree_mem(self, i: int, j: int, value: float):
        """
        Notice that the indices start from 1
        """
        self.tree_mem[i][j] = value

    def init_forest_mem(self):
        node_matrix = [[None for _ in range(len(self.nodes2) + 1)] for _ in range(len(self.nodes1) + 1)]
        for i in range(1, len(self.nodes1)):        # don't +1 because the first element is None
            for j in range(1, len(self.nodes2)):
                u = self.nodes1[i]
                v = self.nodes2[j]
                m = len(u.providers)
                n = len(v.providers)
                node_matrix[i][j] = [[None for _ in range(n + 1)] for _ in range(m + 1)]
                for s in range(1, m + 1):
                    for t in range(1, n + 1):
                        node_matrix[i][j][s][t] = [[0 for _ in range(n - t + 2)] for _ in range(m - s + 2)]
        self.forest_mem = node_matrix

    def get_forest_mem(self, i: int, j: int, s: int, t: int, p: int, q: int) -> float:
        """ Get D(F1[i_s, i_p], F2[j_t, j_q]) """
        res = self.forest_mem[i][j][s][t][p][q]
        assert res is not None
        return res

    def get_forest_mem_matrix(self, i: int, j: int, s: int, t: int) -> List[List[float]]:
        """ Get the matrix for D(F1[i_s, i_p], F2[j_t, j_q]) """
        return self.forest_mem[i][j][s][t]

    def get_min_cost(self) -> float:
        if self.min_cost is None:
            self.compute_cost()
        return self.min_cost

    def get_transforms(self) -> Set[Transform]:
        if self.transforms is None:
            self.compute_transforms()
        return self.transforms

    def compute_cost(self):
        nodes1 = self.nodes1
        nodes2 = self.nodes2

        for i in range(1, len(nodes1)):
            u = nodes1[i]
            self.forest1_to_emtpy[i] = sum([self.get_tree_mem(self.nodes1.index(c), 0) for c in u.providers])
            self.set_tree_mem(i, 0, self.forest1_to_emtpy[i] + self.dist_node(u, None))

        for j in range(1, len(nodes2)):
            v = nodes2[j]
            self.empty_to_forest2[j] = sum([self.get_tree_mem(0, self.nodes2.index(c)) for c in v.providers])
            self.set_tree_mem(0, j, self.empty_to_forest2[j] + self.dist_node(None, v))

        for i in range(1, len(nodes1)):
            for j in range(1, len(nodes2)):
                u = nodes1[i]
                v = nodes2[j]
                m = len(u.providers)
                n = len(v.providers)
                for s in range(1, m + 1):
                    self.compute_dist_forest(i, j, s, 1)
                for t in range(1, n + 1):
                    self.compute_dist_forest(i, j, 1, t)
                self.compute_dist_tree(i, j)

        self.min_cost = self.get_tree_mem(len(nodes1) - 1, len(nodes2) - 1)

    def compute_dist_tree(self, i, j):
        """ Compute D(T1[i], T2[j]), i and j start from 1. 0 is for empty tree. """

        u = self.nodes1[i]
        v = self.nodes2[j]
        m = len(u.providers)
        n = len(v.providers)

        # D(\theta, T2[j]) + min_{1<=r<=n}{D(T1[i], T2[j_r]) - D(\theta, T2[j_r])}
        case1 = self.get_tree_mem(0, j) + min([self.get_tree_mem(i, self.nodes2.index(w)) - self.get_tree_mem(0, self.nodes2.index(w)) for w in v.providers],
                                              default=float('inf'))
        # D(T1[i], \theta) + min_{1<=r<=m}{D(T1[i_r], T2[j]) - D(T1[i_r], \theta)}
        case2 = self.get_tree_mem(i, 0) + min([self.get_tree_mem(self.nodes1.index(w), j) - self.get_tree_mem(self.nodes1.index(w), 0) for w in u.providers],
                                              default=float('inf'))
        # D(F1[i], F2[j]) + \mu(l1[i], l2[j])
        case3 = self.dist_node(u, v)
        if m != 0 and n != 0:
            case3 += self.get_forest_mem(i, j, 1, 1, m, n)
        elif m == 0 and n != 0:
            case3 += self.empty_to_forest2[j]
        elif m != 0 and n == 0:
            case3 += self.forest1_to_emtpy[i]

        dist = min(case1, case2, case3)

        self.set_tree_mem(i, j, dist)

    def compute_dist_forest(self, i, j, s, t):
        """ Compute D(F1[i_s, i_deg(i)], F2[j_t, j_deg(j)]) """
        u = self.nodes1[i]
        v = self.nodes2[j]
        forest1 = u.providers[s-1:]
        forest2 = v.providers[t-1:]
        m = len(forest1)
        n = len(forest2)

        if m == 0 or n == 0:
            return

        matrix = self.get_forest_mem_matrix(i, j, s, t)

        def match_p_children(_p, _q):
            # 5th row in lemma3

            p_node = forest1[_p - 1]        # i_p
            p_index = self.nodes1.index(p_node)
            p_children = p_node.providers   # F1[i_p]

            if len(p_children) == 0:
                # remove all F2[j_k, j_q] as F1[i_p] is empty
                # this case will be considered in 2nd row in lemma3
                return float('inf')

            # \mu(l1[i_p], \lambda)     cost of removing node i_p
            const = self.dist_node(p_node, None)

            min_value = float('inf')
            for k in range(1, _q):      # k can't be _q. is considered in 1st row in lemma3.
                # D(F1[i_s, i_{p-1}], F2[j_t, j_{k-1}]) + D(F1[i_p], F2[j_k, j_q]) =
                # D(F1[i_s, i_{p-1}], F2[j_t, j_{k-1}]) + D(F1[i_p_1, i_p_deg(i_p)], F2[j_k, j_q])
                value = matrix[_p - 1][k - 1] + self.get_forest_mem(p_index, j, 1, k, len(p_children), _q)
                if value < min_value:
                    min_value = value

            return const + min_value

        def match_q_children(_p, _q):
            # 4th row in lemma3

            q_node = forest2[_q - 1]        # j_q
            q_index = self.nodes2.index(q_node)
            q_children = q_node.providers   # F2[j_q]

            if len(q_children) == 0:
                # remove all F1[i_k, i_p] as F2[j_q] is empty
                # this case will be considered in 1st row in lemma3
                return float('inf')

            # \mu(\lambda, l2[j_q])     cost of adding node j_q
            const = self.dist_node(None, q_node)

            min_value = float('inf')
            for k in range(1, _p):      # k can't be _p. is considered in 2nd row in lemma3.
                # D(F1[i_s, i_{k-1}], F2[j_t, j_{q-1}]) + D(F1[i_k, i_p], F2[j_q]) =
                # D(F1[i_s, i_{k-1}], F2[j_t, j_{q-1}]) + D(F1[i_k, i_p], F2[j_q_1, j_q_deg(j_q)])
                value = matrix[k - 1][_q - 1] + self.get_forest_mem(i, q_index, k, 1, _p, len(q_children))
                if value < min_value:
                    min_value = value

            return const + min_value

        for p in range(1, m + 1):
            matrix[p][0] = matrix[p - 1][0] + self.get_tree_mem(self.nodes1.index(forest1[p - 1]), 0)
        for q in range(1, n + 1):
            matrix[0][q] = matrix[0][q - 1] + self.get_tree_mem(0, self.nodes2.index(forest2[q - 1]))
        for p in range(1, m + 1):
            for q in range(1, n + 1):
                p_index = self.nodes1.index(forest1[p - 1])
                q_index = self.nodes2.index(forest2[q - 1])
                matrix[p][q] = min(
                    # D(F1[i_1, i_{p-1}], F2[j_1, j_q]) + D(T1[i_p], \theta)
                    matrix[p - 1][q] + self.get_tree_mem(p_index, 0),
                    # D(F1[i_1, i_p], F2[j_1, j_{q-1}]) + D(\theta, T2[j_q])
                    matrix[p][q - 1] + self.get_tree_mem(0, q_index),
                    # D(F1[i_1, i_{p-1}], F2[j_1, j_{q-1}]) + D(T1[i_p], T2[j_q])
                    matrix[p - 1][q - 1] + self.get_tree_mem(p_index, q_index),
                    match_p_children(p, q),
                    match_q_children(p, q),
                )

    def dist_node(self, node1: Optional[PlanNode], node2: Optional[PlanNode]):
        assert not (node1 is None and node2 is None), 'node1 and node2 cannot be both None'
        if node1 is None or node2 is None:
            return 1    # delete or insert
        if node1.name == node2.name:
            if node1.str_ == node2.str_:
                return 0    # unchange
            else:
                return 0.5  # modify
        else:
            return 1    # replace

    def get_subtree_nodes(self, tree: PlanNode):
        """Get all nodes in the subtree of the given tree in postorder."""
        nodes = []
        for child in tree.providers:
            nodes.extend(self.get_subtree_nodes(child))
        nodes.append(tree)
        return nodes

    def compute_transforms(self):
        """ Backtracking to compute the transforms """
        transforms = self.transforms = set()

        min_cost = self.get_min_cost()




