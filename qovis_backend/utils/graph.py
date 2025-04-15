from functools import cached_property


class Graph:
    def __init__(self, vertices: list):
        self.vertices = vertices
        self.vertex2id = {v: i for i, v in enumerate(vertices)}
        self.adjacency = [[] for _ in range(len(vertices))]

    def add_edge(self, v1, v2):
        v1_id = self.vertex2id[v1]
        v2_id = self.vertex2id[v2]
        if v2_id not in self.adjacency[v1_id]:
            self.adjacency[v1_id].append(v2_id)
        if v1_id not in self.adjacency[v2_id]:
            self.adjacency[v2_id].append(v1_id)

    @cached_property
    def independent_sets(self) -> list[list]:
        # find all independent sets
        independent_sets: list[set] = []
        for i in range(len(self.vertices)):
            valid_set = set(range(i, len(self.vertices)))
            independent_sets.extend(self._collect_independent_set(i, valid_set, set()))
        # remove duplicate sets
        independent_sets = self._remove_duplicate_sets(independent_sets)
        # remove subsets
        independent_sets = self._remove_subsets(independent_sets)
        # convert to list
        return [[self.vertices[i] for i in s] for s in independent_sets]

    def _collect_independent_set(self, cur_index: int, valid_set: set[int], selected: set[int]) -> list[set]:
        if cur_index >= len(self.vertices):
            return [selected]
        sets = []
        # do not select current index
        sets.extend(self._collect_independent_set(cur_index + 1, valid_set, selected))
        # select current index
        if cur_index in valid_set:
            new_valid_set = valid_set - set(self.adjacency[cur_index]) - {cur_index}
            new_selected = selected | {cur_index}
            sets.extend(self._collect_independent_set(cur_index + 1, new_valid_set, new_selected))
        return sets

    @staticmethod
    def _remove_duplicate_sets(sets: list[set]) -> list[set]:
        results = []
        hash_set_dict = {}
        for s in sets:
            h = sum([2 ** i for i in s])
            if h not in hash_set_dict:
                hash_set_dict[h] = s
        for s in hash_set_dict.values():
            results.append(s)
        return results

    @staticmethod
    def _remove_subsets(sets: list[set]) -> list[set]:
        results = []
        for s1 in sets:
            is_subset = False
            for s2 in sets:
                if s1 == s2:
                    continue
                if s1.issubset(s2):
                    is_subset = True
                    break
            if not is_subset:
                results.append(s1)
        return results

    def print_adj(self):
        print('Vertices:', self.vertices)
        print('Adjacency:')
        for i, adj in enumerate(self.adjacency):
            row = [1 if j in adj else 0 for j in range(len(self.vertices))]
            print('\t'.join([str(v) for v in row]))


def test_graph():
    graph = Graph([0, 1, 2, 3, 4, 5, 6])
    graph.add_edge(0, 1)
    graph.add_edge(0, 2)
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(1, 4)
    graph.add_edge(2, 4)
    graph.add_edge(3, 4)
    graph.add_edge(3, 5)
    graph.add_edge(4, 5)
    graph.add_edge(4, 6)
    graph.add_edge(5, 6)
    print(graph.independent_sets)

    graph = Graph(['a', 'b', 'c'])
    graph.add_edge('a', 'b')
    graph.add_edge('a', 'c')
    graph.add_edge('b', 'c')
    print(graph.independent_sets)

    graph = Graph(['a', 'b', 'c', 'd'])
    graph.add_edge('a', 'b')
    graph.add_edge('a', 'c')
    graph.add_edge('a', 'd')
    graph.add_edge('b', 'c')
    graph.add_edge('b', 'd')
    graph.print_adj()
    print(graph.independent_sets)
