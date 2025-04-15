from typing import List, Dict, Set


class D2vConverter:
    def __init__(self):
        # node.idx -> s_idx
        self.node_idx_to_subgraph_idx = {}
        # s_idx -> child s_idx
        self.child_graphs_dict: Dict[int, Set[int]] = {}
        # s_idx -> all descendant s_idx
        self.sub_graphs_lst: List[Set[int]] = []
        # node.idx -> depth
        self.depth_dict: Dict[int, int] = {}
        self.max_depth: int = -1

    def extract(self) -> List[List[bool]]:
        # Weisfeiler-Lehman (WL) algorithm

        cur_s_idx = 0

        for node in self.dag.nodes:
            self.node_idx_to_subgraph_idx[node.idx] = cur_s_idx
            self.child_graphs_dict[cur_s_idx] = set()
            self.sub_graphs_lst.append(set())
            cur_s_idx += 1

        self.compute_depth()

        # depth = 0 === single node. we already added them
        subgraph_depth = 1
        # node.idx -> tmp subgraph s_idx
        tmp_s_idx_dict = self.node_idx_to_subgraph_idx.copy()

        cur_roots = [node for node in self.dag.nodes]

        while True:
            cur_roots = list(filter(lambda v: self.depth_dict[v.idx] >= subgraph_depth, cur_roots))

            if len(cur_roots) == 0:
                break

            new_s_idx_lst = list(range(cur_s_idx, cur_s_idx + len(cur_roots)))

            # collect child sub-graphs
            for root, s_idx in zip(cur_roots, new_s_idx_lst):
                child_s_idx_set = {tmp_s_idx_dict[p.idx] for p in root.precursors}
                self.child_graphs_dict[s_idx] = child_s_idx_set

                s = child_s_idx_set.copy()
                for child_s_idx in child_s_idx_set:
                    s.update(self.sub_graphs_lst[child_s_idx])
                self.sub_graphs_lst.append(s)

            # update tmp s_idx for each node
            for root, s_idx in zip(cur_roots, new_s_idx_lst):
                tmp_s_idx_dict[root.idx] = s_idx

            cur_s_idx += len(cur_roots)
            subgraph_depth += 1

    def compute_depth(self):
        depth = -1
        cur_layer = list(filter(lambda v: len(v.precursors) == 0, self.dag.nodes))

        while len(cur_layer) != 0:
            depth += 1
            nxt_layer = []
            for node in cur_layer:
                if node.idx in self.depth_dict:
                    continue
                self.depth_dict[node.idx] = depth
                nxt_layer += node.successors
            cur_layer = nxt_layer

        self.max_depth = depth

    def get_sub_graphs_lst(self):
        return self.sub_graphs_lst

    def convert(self, data: Dict[str, List[float]]) -> List[float]:
        s_idx_to_time_lst = {}
        duration = 0        # duration of whole execution
        for node in self.dag.nodes:
            time_lst = data[node.name]
            s_idx = self.node_idx_to_subgraph_idx[node.idx]
            s_idx_to_time_lst[s_idx] = time_lst
            duration = max(duration, time_lst[0], time_lst[1])

        assert duration != 0

        vec = []

        for s_idx in range(len(self.dag.nodes)):
            start, end = s_idx_to_time_lst[s_idx]
            # vec.append(end - start)
            vec.append((end - start) / duration)
            # vec.append([start / duration, end / duration])

        for s_idx in range(len(self.dag.nodes), len(self.sub_graphs_lst)):
            start, end = float('inf'), float('-inf')
            for child_s_idx in self.child_graphs_dict[s_idx]:
                tmp_start, tmp_end = s_idx_to_time_lst[child_s_idx]
                start = min(tmp_start, start)
                end = max(tmp_end, end)
            # vec.append(end - start)
            vec.append((end - start) / duration)
            # vec.append([start / duration, end / duration])
            s_idx_to_time_lst[s_idx] = (start, end)

        # vec = [int(v) for v in vec]
        # print(vec)

        return vec
