import time
from functools import cached_property, reduce
from typing import Optional

from trans.algo.rule_list import RULE_DICT
from trans.plan.param.base_param import BaseParam
from trans.plan.plan_match import PlanMatch
from trans.plan.plan_node import PlanNode
from trans.plan.query_plan import QueryPlan
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.rule import Rule
from trans.rule.trans_link import TransLink


class TransPath:
    def __init__(self, success: bool,
                 plan_path: list[QueryPlan],
                 t_dst: QueryPlan,
                 rule_path: list[Rule],
                 matches: list[tuple[PlanMatch, Optional[PlanMatch]]]):
        self.success = success
        self.plan_path = plan_path
        self.t_dst_bk = t_dst
        self.rule_path = rule_path
        self.matches = matches

    @cached_property
    def t_src(self) -> QueryPlan:
        return self.plan_path[0]

    @cached_property
    def t_dst(self) -> QueryPlan:
        return self.plan_path[-1]

    def get_links(self) -> list[TransLink]:
        if not self.success:
            return self._get_possible_links(self.t_src, self.t_dst)

        step_cnt = len(self.plan_path) - 1

        if step_cnt == 0:
            # two plans are the same
            return self._build_eq_links(self.t_src.root, self.t_dst.root)

        step_links_list: list[list[TransLink]] = []
        for i in range(step_cnt):
            t0 = self.plan_path[i]
            t1 = self.plan_path[i + 1]
            rule = self.rule_path[i]
            match0, match1 = self.matches[i]
            step_links = self._get_step_links(t0, t1, rule, match0, match1)
            step_links_list.append(step_links)

        links = reduce(lambda x, y: self.merge_links(x, y), step_links_list)

        return links

    @classmethod
    def _get_possible_links(cls, t0: QueryPlan, t1: QueryPlan) -> list[TransLink]:
        param_str2loc_info_list: dict[str, list[tuple[PlanNode, str, Optional[int]]]] = {}
        for node0 in t0.node_dict.values():
            params = node0.dump_params()
            for name, value in params:
                for idx, param_str in enumerate(value):
                    param_str2loc_info_list.setdefault(value[idx], []).append((node0, name, idx))
        links = []
        for node1 in t1.node_dict.values():
            params = node1.dump_params()
            for name1, value in params:
                for idx1, param_str1 in enumerate(value):
                    if param_str1 not in param_str2loc_info_list:
                        continue
                    for node0, name0, idx0 in param_str2loc_info_list[param_str1]:
                        links.append(TransLink.mk_peq(node0, node1, name0, name1, idx0, idx1))
        for link in links:
            link.rules = [TransLink.GUESS_STEP]
        return links

    @classmethod
    def _get_step_links(cls, t0: QueryPlan, t1: QueryPlan, rule: Rule,
                        match0: PlanMatch, match1: Optional[PlanMatch]) -> list[TransLink]:
        links = []

        if match1 is None:
            # remove rule
            # the above part
            if t0.root is not match0.target_root:
                # match1 exists and the replacement does not locate at the root
                # all above part should be the same
                links.extend(cls._build_eq_links_with_pruning_one_side(t0.root, t1.root, match0.target_root))

            # the below part
            res = cls._find_cut_point_at_the_same_time(t0.root, t1.root, match0.target_root)
            assert res is not None
            node0, node1, _ = res
            # the remove part is a chain, and won't be the leaf (for now)
            while node0.children[0].vid in match0.target_to_pattern:
                node0 = node0.children[0]
            # the below part should be the same
            node0 = node0.children[0]
            links.extend(cls._build_eq_links_with_pruning_one_side(node0, node1, match0.target_root))

        else:
            # the above part
            if t0.root is not match0.target_root:
                # match1 exists and the replacement does not locate at the root
                # all above part should be the same
                links.extend(cls._build_eq_links_with_pruning(t0.root, t1.root, match0.target_root, match1.target_root))

            # the below part
            rel_eq_constraints: list[RelEq] = list(filter(lambda x: isinstance(x, RelEq), rule.trans_constraints))
            for c in rel_eq_constraints:
                if c.need_computation():
                    continue        # computed alreadly
                node0 = match0.get_target_node(c.rel0.owner)      # the src node in variable "t0"
                rel0_index = c.rel0.get_index()

                node1 = match1.get_target_node(c.rel1.owner)
                rel1_index = c.rel1.get_index()

                child0 = node0.children[rel0_index]
                child1 = node1.children[rel1_index]
                links.extend(cls._build_eq_links(child0, child1))

            # the changed part
            for c in rule.trans_constraints:
                links.extend(c.get_links(match0, match1))

        # set rule name to links
        for link in links:
            if link.kind == TransLink.LinkKind.EQ:
                link.rules = [TransLink.UNCHANGED_STEP]
            else:
                assert link.kind == TransLink.LinkKind.CH
                link.rules = [rule]

        return links

    @classmethod
    def _build_eq_links(cls, node0: PlanNode, node1: PlanNode) -> list[TransLink]:
        assert node0.semantically_equals(node1)
        links = node0.build_eq_links(node1)
        for link in links:
            link.rules = [TransLink.UNCHANGED_STEP]
        for c0, c1 in zip(node0.children, node1.children):
            links.extend(cls._build_eq_links(c0, c1))
        return links

    @classmethod
    def _build_eq_links_with_pruning(cls, node0: PlanNode, node1: PlanNode,
                                     stop_node0: PlanNode, stop_node1: PlanNode) -> list[TransLink]:
        if node0 is stop_node0 and node1 is stop_node1:
            return []       # the subtree rooted at node0 and node1 are changed by the rule
        # node0 and node1 can only be the stop node at the same time
        assert node0 is not stop_node0 and node1 is not stop_node1
        links = node0.build_eq_links(node1)
        for c0, c1 in zip(node0.children, node1.children):
            links.extend(cls._build_eq_links_with_pruning(c0, c1, stop_node0, stop_node1))
        return links

    @classmethod
    def _build_eq_links_with_pruning_one_side(cls, node0: PlanNode, node1: PlanNode,
                                              stop_node0: PlanNode) -> list[TransLink]:
        if node0 is stop_node0:
            return []       # the subtree rooted at node0 and node1 are changed by the rule
        links = node0.build_eq_links(node1)
        for c0, c1 in zip(node0.children, node1.children):
            links.extend(cls._build_eq_links_with_pruning_one_side(c0, c1, stop_node0))
        return links

    @classmethod
    def _find_cut_point_at_the_same_time(cls, node0: PlanNode,
                                         node1: PlanNode,
                                         stop_node0: PlanNode) -> Optional[tuple[PlanNode, PlanNode, int]]:
        """ The nth child of node0 and node1 are different. """
        if node0 is stop_node0:
            return node0, node1, 0  # now it can only be 0
        for c0, c1 in zip(node0.children, node1.children):
            res = cls._find_cut_point_at_the_same_time(c0, c1, stop_node0)
            if res is not None:
                return res
        return None

    @classmethod
    def _find_parent(cls, node: PlanNode, target: PlanNode) -> Optional[PlanNode]:
        if node is target:
            return None
        if target in node.children:
            return node
        for child in node.children:
            parent = cls._find_parent(child, target)
            if parent is not None:
                return parent
        return None

    # @classmethod
    # def merge_step_links(cls, links0: list[TransLink], links1: list[TransLink]) -> list[TransLink]:
    #     # t0 -> t1 -> t2
    #     t1_vid_to_links0: dict[int, list[TransLink]] = {}
    #     for link in links0:
    #         t1_vid_to_links0.setdefault(link.node1.vid, []).append(link)
    #     t1_vid_to_links1: dict[int, list[TransLink]] = {}
    #     for link in links1:
    #         t1_vid_to_links1.setdefault(link.node0.vid, []).append(link)
    #
    #     result_links = []
    #     for vid1, links in t1_vid_to_links0.items():
    #         if vid1 not in t1_vid_to_links1:
    #             continue
    #         for link0 in links:
    #             for link1 in t1_vid_to_links1[vid1]:
    #                 new_link = link0.merge(link1)
    #                 result_links.append(new_link)
    #
    #     return result_links

    @classmethod
    def merge_links(cls, links0: list[TransLink], links1: list[TransLink]) -> list[TransLink]:
        # t0 -> t1 -> t2
        # (vid (in t1), param name, param idx) -> links
        links0_dict: dict[tuple[int, str, int], list[TransLink]] = {}
        for link in links0:
            key = (link.node1.vid, link.param1, link.param_idx1)
            links0_dict.setdefault(key, []).append(link)
        links1_dict: dict[tuple[int, str, int], list[TransLink]] = {}
        for link in links1:
            key = (link.node0.vid, link.param0, link.param_idx0)
            links1_dict.setdefault(key, []).append(link)

        result_links = []
        for key, links in links0_dict.items():
            if key not in links1_dict:
                continue
            links_tmp = links1_dict[key]
            for link0 in links:
                for link1 in links_tmp:
                    new_link = link0.merge(link1)
                    result_links.append(new_link)

        return result_links

    @staticmethod
    def mk_transform_path(t_src, t_dst, rule_path: Optional[list[Rule]]) -> 'TransPath':
        if not rule_path:
            return TransPath(False, [t_src, t_dst], t_dst, [], [])

        # state idx in last step, resulted plan, src match, dst match (matching resulted plan)
        SearchState = tuple[int, QueryPlan, Optional[PlanMatch], Optional[PlanMatch]]
        search_space: list[list[SearchState]] = [[] for _ in range(len(rule_path) + 1)]
        search_space[0].append((-1, t_src, None, None))
        for step_cnt, rule in enumerate(rule_path):
            for parent_idx, (_, parent_plan, _, _) in enumerate(search_space[step_cnt]):
                for new_plan, src_match, dst_match in rule.apply_and_return_match(parent_plan):
                    search_space[step_cnt + 1].append((parent_idx, new_plan, src_match, dst_match))

        for idx, (_, plan, _, _) in enumerate(search_space[-1]):
            if not plan.semantically_equals(t_dst):
                continue
            plan.semantically_equals(t_dst)
            plan_path = []
            matches = []
            from_idx = idx
            for step_cnt in range(len(rule_path), 0, -1):
                from_idx, plan, src_match, dst_match = search_space[step_cnt][from_idx]
                plan_path.insert(0, plan)
                matches.insert(0, (src_match, dst_match))
            # plan_path[-1] is not the same object as t_dst, so matches should be updated
            # but the vid is the same (we only return this to the frontend)
            return TransPath(True, [t_src] + plan_path, t_dst, rule_path, matches)

        return TransPath(False, [t_src, t_dst], t_dst, [], [])

    def dump(self):
        return {
            'success': self.success,
            'rules': [r.name for r in self.rule_path],
            'links': [link.dump() for link in self.get_links()],
        }
