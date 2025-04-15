from trans.plan.operator.input_like import InputLike
from trans.plan.param.base_param import BaseParam
from trans.plan.plan_node import PlanNode


class JoinUtils:
    @staticmethod
    def get_join_order(root: PlanNode) -> list[str]:
        """ Return the list of relation names in the join order. """

        def _dfs(node: PlanNode):
            res = []
            if issubclass(node.__class__, InputLike):
                rels = node.params[BaseParam.Kind.REL]
                assert len(rels) != 0
                res.append(rels[0].name)
            else:
                for child in node.children:
                    res.extend(_dfs(child))
            return res

        return _dfs(root)

    @staticmethod
    def get_min_join_order_swap_cnt(t0: PlanNode, t1: PlanNode) -> int:
        lst0 = JoinUtils.get_join_order(t0)
        lst1 = JoinUtils.get_join_order(t1)
        if len(lst0) != len(lst1) or set(lst0) != set(lst1):
            return 0
        if lst0 == lst1:
            return 0
        # minimum swap count that makes lst0 == lst1
        value_to_id = {v: i for i, v in enumerate(lst0)}
        lst0 = [value_to_id[v] for v in lst0]
        lst1 = [value_to_id[v] for v in lst1]

        target_idx_map = {v: i for i, v in enumerate(lst1)}
        loop_cnt = 0
        visited = [False] * len(lst0)
        for i in range(len(lst0)):
            if visited[i]:
                continue
            j = i
            while not visited[j]:
                visited[j] = True
                j = target_idx_map[lst0[j]]
            loop_cnt += 1
        return len(lst0) - loop_cnt

