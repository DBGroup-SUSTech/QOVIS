from typing import Optional, Any, TypeVar, Generic

from trans.plan.param.base_param import BaseParam
from trans.plan.plan_node import PlanNode
from trans.plan.query_plan import QueryPlan

T = TypeVar('T')


class PlanMap(Generic[T]):
    def __init__(self):
        # plan_hash -> list[tuple[plan, T]]
        self.dict: dict[int, list[tuple[QueryPlan, T]]] = {}
        # self.dict: dict[int, T] = {}
        self.size = 0

        self.op_kind_to_id: dict[str, int] = {}
        self.next_id = 0

        # list all kinds of params
        self.param_kinds: list[BaseParam.Kind] = list(BaseParam.Kind)
        self.param_dicts: list[dict[str, int]] = [{} for _ in self.param_kinds]
        self.next_param_id_dict: list[int] = [0 for _ in self.param_kinds]

    def __len__(self):
        return self.size

    def __contains__(self, plan: QueryPlan):
        return self[plan] is not None

    def __setitem__(self, plan: QueryPlan, value: T):
        plan_hash = self._to_hash_with_update(plan)
        block = self.dict.setdefault(plan_hash, [])
        for i in range(len(block)):
            saved_plan, _ = block[i]
            if saved_plan.semantically_equals(plan):
                block[i] = (saved_plan, value)
                return
        block.append((plan, value))
        self.size += 1

    def __getitem__(self, plan: QueryPlan) -> Optional[T]:
        plan_hash = self._to_hash(plan)
        if plan_hash is None or plan_hash not in self.dict:
            return None
        for saved_plan, value in self.dict[plan_hash]:
            if saved_plan.semantically_equals(plan):
                return value
        return None

    def __delitem__(self, plan: QueryPlan):
        plan_hash = self._to_hash(plan)
        if plan_hash is None or plan_hash not in self.dict:
            return
        block = self.dict[plan_hash]
        for i in range(len(block)):
            saved_plan, _ = block[i]
            if saved_plan.semantically_equals(plan):
                del block[i]
                self.size -= 1
                return

    # def __setitem__(self, plan: QueryPlan, value: T):
    #     plan_hash = self._to_hash_with_update(plan)
    #     if plan_hash not in self.dict:
    #         self.size += 1
    #     self.dict[plan_hash] = value
    #
    # def __getitem__(self, plan: QueryPlan) -> Optional[T]:
    #     plan_hash = self._to_hash(plan)
    #     if plan_hash is None or plan_hash not in self.dict:
    #         return None
    #     return self.dict[plan_hash]
    #
    # def __delitem__(self, plan: QueryPlan):
    #     plan_hash = self._to_hash(plan)
    #     if plan_hash is None or plan_hash not in self.dict:
    #         return
    #     del self.dict[plan_hash]
    #     self.size -= 1

    def _to_hash_with_update(self, plan: QueryPlan) -> int:
        return hash(self._collect_features_list_with_update(plan))

    def _collect_features_list_with_update(self, plan: QueryPlan) -> tuple[tuple[int]]:
        """ Returns the list of features of each node in pre-order traversal. """
        features_list: list[tuple[int]] = []
        stk = [plan.root]
        while stk:
            node = stk.pop()
            features_list.append(self._get_features_with_update(node))
            stk.extend(node.children)
        return tuple(features_list)

    def _get_features_with_update(self, node: PlanNode) -> tuple[int]:
        # get op id
        op_kind = node.name
        if op_kind not in self.op_kind_to_id:
            self.op_kind_to_id[op_kind] = self.next_id
            self.next_id += 1
        op_id = self.op_kind_to_id[op_kind]

        # get each param str id
        param_ids: list[int] = []
        for i in range(len(self.param_kinds)):
            kind = self.param_kinds[i]
            param = node.params.get(kind)
            param_str = ','.join(p.to_hash_str() for p in param) if param is not None else ''
            param_str_to_id = self.param_dicts[i]
            if param_str not in param_str_to_id:
                param_str_id = self.next_param_id_dict[i]
                param_str_to_id[param_str] = param_str_id
                self.next_param_id_dict[i] += 1
            else:
                param_str_id = param_str_to_id[param_str]
            param_ids.append(param_str_id)

        return op_id, *param_ids

    def _to_hash(self, plan: QueryPlan) -> Optional[int]:
        feature_list = self._collect_features_list(plan)
        return hash(feature_list) if feature_list is not None else None

    def _collect_features_list(self, plan: QueryPlan) -> Optional[tuple[tuple[int]]]:
        """ Returns the list of features of each node in pre-order traversal. """
        features_list: list[tuple[int]] = []
        stk = [plan.root]
        while stk:
            node = stk.pop()
            features = self._get_features(node)
            if features is None:
                return None
            features_list.append(features)
            stk.extend(node.children)
        return tuple(features_list)

    def _get_features(self, node: PlanNode) -> Optional[tuple[int]]:
        # get op id
        op_kind = node.name
        if op_kind not in self.op_kind_to_id:
            return None
        op_id = self.op_kind_to_id[op_kind]

        # get each param str id
        param_ids: list[int] = []
        for i in range(len(self.param_kinds)):
            kind = self.param_kinds[i]
            param = node.params.get(kind)
            param_str = ','.join(p.to_hash_str() for p in param) if param is not None else ''
            param_str_to_id = self.param_dicts[i]
            if param_str not in param_str_to_id:
                return None
            else:
                param_str_id = param_str_to_id[param_str]
            param_ids.append(param_str_id)

        return op_id, *param_ids
