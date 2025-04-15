class DisjointSet:
    def __init__(self, elements: list):
        self.elements = elements
        self.element2id = {e: i for i, e in enumerate(elements)}
        self.parent = [i for i in range(len(elements))]

    def find(self, element):
        el_id = self.element2id[element]
        return self.elements[self._find(el_id)]

    def _find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self._find(self.parent[x])
        return self.parent[x]

    def union(self, el1, el2):
        x = self.element2id[el1]
        y = self.element2id[el2]

        x_root = self._find(x)
        y_root = self._find(y)

        if x_root != y_root:
            self.parent[x_root] = y_root

    def get_groups(self) -> list[list]:
        group_dict = {}
        for i in range(len(self.elements)):
            root = self._find(i)
            if root not in group_dict:
                group_dict[root] = []
            group_dict[root].append(i)
        results = []
        for group in group_dict.values():
            results.append([self.elements[i] for i in group])
        return results


def inner_test():
    ds = DisjointSet([0, 1, 2, 3, 'x'])
    ds.union(0, 1)
    ds.union(1, 2)
    ds.union(3, 'x')
    print(ds.find(0))
    print(ds.find(1))
    print(ds.find(2))
    print(ds.find(3))
    print(ds.find('x'))
    print(ds.get_groups())


if __name__ == '__main__':
    inner_test()