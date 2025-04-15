import sys
from typing import Optional, Generator

from trans.plan.plan_match import PlanMatch
from trans.plan.query_plan import QueryPlan
from trans.plan.plan_node import PlanNode
from trans.rule.constraint.impl.rel_eq import RelEq
from trans.rule.constraint.src_constraint import ValidConstraint
from trans.rule.constraint.trans_constraint import TransConstraint


class Rule:
    OPT: str = "optimization"

    def __init__(self, name: str, category: str,
                 src: PlanNode, dst: Optional[PlanNode],
                 *,
                 src_constraints: list[ValidConstraint] = None,
                 trans_constraints: list[TransConstraint] = None,
                 dst_constraints: list[ValidConstraint] = None):
        self.name = name
        self.category: str = category
        self.src = src
        self.dst = dst
        self.src_constraints: list[ValidConstraint] = src_constraints if src_constraints is not None else []
        self.trans_constraints: list[TransConstraint] = trans_constraints if trans_constraints is not None else []
        self.dst_constraints: list[ValidConstraint] = dst_constraints if dst_constraints is not None else []

        # init pattern
        for i, node in enumerate(self.src.collect_all()):
            node.assign(None, -i-1, 'PatternNode', None, None)
        if self.dst is not None:
            for i, node in enumerate(self.dst.collect_all()):
                node.assign(None, -i-1, 'PatternNode', None, None)
        else:
            assert len(self.dst_constraints) == 0, "dst_constraints should be empty if dst is None"

    def apply(self, plan: QueryPlan):
        matches = self.find_all_matches(plan, self.src)
        for match in matches:
            if self.dst is None:
                # just remove the matched part
                new_plan = self.remove(plan, match)
                if new_plan is None:
                    continue
                if not new_plan.is_valid():
                    raise Exception("Invalid plan after applying rule.")
                yield new_plan
            else:
                repl_matches = self.create_replacement(match)
                for repl_match in repl_matches:
                    new_plan = self.replace(plan, match, repl_match.target, repl_match)
                    if new_plan is None:
                        continue
                    # check dst_constraints
                    if not all(c.check(repl_match) for c in self.dst_constraints):
                        continue
                    if not new_plan.is_valid():
                        new_plan.is_valid()
                        raise Exception("Invalid plan after applying rule.")
                    yield new_plan

    def apply_with_index(self, plan: QueryPlan, match_index: int):
        matches = self.find_all_matches(plan, self.src)

        matches = [list(matches)[match_index]]

        for match in matches:
            if self.dst is None:
                # just remove the matched part
                new_plan = self.remove(plan, match)
                if new_plan is None:
                    continue
                if not new_plan.is_valid():
                    raise Exception("Invalid plan after applying rule.")
                yield new_plan
            else:
                repl_matches = self.create_replacement(match)
                for repl_match in repl_matches:
                    new_plan = self.replace(plan, match, repl_match.target, repl_match)
                    if new_plan is None:
                        continue
                    # check dst_constraints
                    if not all(c.check(repl_match) for c in self.dst_constraints):
                        continue
                    if not new_plan.is_valid():
                        raise Exception("Invalid plan after applying rule.")
                    yield new_plan

    def apply_and_return_match(self, plan: QueryPlan) -> Generator[tuple[QueryPlan, PlanMatch, Optional[PlanMatch]], None, None]:
        matches = self.find_all_matches(plan, self.src)
        for match in matches:
            if self.dst is None:
                # just remove the matched part
                new_plan = self.remove(plan, match)
                if new_plan is None:
                    continue
                if not new_plan.is_valid():
                    raise Exception("Invalid plan after applying rule.")
                yield new_plan, match, None
            else:
                repl_matches = self.create_replacement(match)
                for repl_match in repl_matches:
                    new_plan = self.replace(plan, match, repl_match.target, repl_match)
                    if new_plan is None:
                        continue
                    # check dst_constraints
                    if not all(c.check(repl_match) for c in self.dst_constraints):
                        continue
                    if not new_plan.is_valid():
                        raise Exception("Invalid plan after applying rule.")
                    yield new_plan, match, repl_match

    def find_all_matches(self, plan: QueryPlan, pattern: PlanNode):
        """ Find the subtrees in the plan that match the pattern. """
        root = plan.root
        if root is None:
            return

        for node in root.collect_all():
            if not Rule.match_node(node, pattern):
                continue
            match = PlanMatch(plan.root, pattern, node)
            if all(c.check(match) for c in self.src_constraints):
                yield match

    @staticmethod
    def match_node(node: PlanNode, pattern: PlanNode) -> bool:
        """ Check if the node matches the pattern without checking the constraints. """
        if not pattern.match(node):
            return False
        if len(pattern.children) > 0:
            if len(node.children) != len(pattern.children):
                return False
            for child, p_child in zip(node.children, pattern.children):
                if p_child is None:
                    continue    # Any node
                if not Rule.match_node(child, p_child):
                    return False
        return True

    def create_replacement(self, match: PlanMatch) -> list[PlanMatch]:
        """ Create a replacement using the pattern and the match. """
        assert self.dst is not None, "Cannot create replacement for a deletion rule."
        repl = self.dst.mk_tree(match, False)
        cur_level = [PlanMatch(repl, self.dst, repl)]
        for c in self.trans_constraints:
            next_level = []
            for repl_match in cur_level:
                next_level.extend(c.apply(match, repl_match))
            cur_level = next_level
        return cur_level

    def replace(self, plan: QueryPlan, match: PlanMatch, repl: PlanNode, repl_match: PlanMatch) -> Optional[QueryPlan]:
        """ Replace the matched subtree with the replacement. """

        new_plan = plan.copy()
        target_root = new_plan.node_dict[match.target_root.vid]

        # process the above part
        if target_root is new_plan.root:
            new_plan.root = repl
        else:
            # find the parent of the target root
            parent = self._find_parent(new_plan.root, target_root)
            assert parent is not None
            parent.children[parent.children.index(target_root)] = repl

        # process the below parts (defined by RelEq)
        # get all RelEq constraints
        rel_eq_constraints: list[RelEq] = list(filter(lambda x: isinstance(x, RelEq), self.trans_constraints))
        for c in rel_eq_constraints:
            if c.need_computation():
                continue        # has been computed
            origin_node0 = match.get_target_node(c.rel0.owner)      # the src node in variable "plan"
            node0 = new_plan.node_dict[origin_node0.vid]            # the corresponding node in variable "new_plan"
            rel0_index = c.rel0.get_index()

            node1 = repl_match.get_target_node(c.rel1.owner)
            rel1_index = c.rel1.get_index()

            if node1.n_child == 0:
                pass
            else:
                while len(node1.children) <= rel1_index:
                    node1.children.append(None)
                node1.children[rel1_index] = node0.children[rel0_index].copy_tree()

        # reassign vid
        new_plan.root.reassign_vid()
        # update the node_dict
        new_plan.node_dict = {n.vid: n for n in new_plan.root.collect_all()}

        # new_plan.complete_param()

        try:
            new_plan.complete_param()
        except Exception as e:
            sys.stderr.write(f"Create new plan failed: {e}\n")
            return None

        return new_plan

    def remove(self, plan: QueryPlan, match: PlanMatch) -> Optional[QueryPlan]:
        """ The matched part must be chain-like. """
        new_plan = plan.copy()
        target_root = new_plan.node_dict[match.target_root.vid]

        # get the tail of the matched part
        tail_p = match.pattern     # self.src
        while len(tail_p.children) > 0:
            tail_p = tail_p.children[0]
        tail_origin = match.get_target_node(tail_p)     # node in variable "plan"
        tail = new_plan.node_dict[tail_origin.vid]   # node in variable "new_plan"

        if target_root is new_plan.root:
            #  target_root    =>    B
            #    |
            #  tail
            #    |
            #    B
            assert len(tail.children) != 0, "The matched part is the whole plan."
            assert len(tail.children) == 1, "The matched part is not chain-like."
            new_plan.root = tail.children[0]
        else:
            #    A            =>    A
            #    |                  |
            #  target_root          B
            #    |
            #  tail
            #    |
            #    B
            parent = self._find_parent(new_plan.root, target_root)  # A
            assert parent is not None
            if len(tail.children) == 0:
                # B is None
                raise Exception(f"Node {tail} has no child.")
            else:
                # B is not None
                assert len(tail.children) == 1, "The matched part is not chain-like."
                parent.children[parent.children.index(target_root)] = tail.children[0]

        # reassign vid
        new_plan.root.reassign_vid()
        # update the node_dict
        new_plan.node_dict = {n.vid: n for n in new_plan.root.collect_all()}

        try:
            new_plan.complete_param()
        except Exception as e:
            sys.stderr.write(f"Create new plan failed: {e}\n")
            return None

        return new_plan

    def _find_parent(self, node: PlanNode, target: PlanNode) -> Optional[PlanNode]:
        if node is target:
            return None
        if target in node.children:
            return node
        for child in node.children:
            parent = self._find_parent(child, target)
            if parent is not None:
                return parent
        return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

