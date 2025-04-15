from trans.plan.operator.impl.serialize_from_object import SerializeFromObject
from trans.plan.param.attributes import Attributes
from trans.plan.plan_match import PlanMatch
from trans.plan.plan_node import PlanNode

from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class SfoPrune(TransConstraint):
    def __init__(self, reqs: Attributes, node0: SerializeFromObject, node1: SerializeFromObject):
        super().__init__()
        self.reqs = reqs
        self.node0 = node0
        self.node1 = node1

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        """
        target_match.target is the target plan tree.
        target_match.pattern is the src pattern of rule.
        repl_match.target is the repl plan tree.
        repl_match.pattern is the dst pattern of rule.
        """
        reqs = target_match.get_target_attrs(self.reqs)
        node0 = target_match.get_target_node(self.node0)
        node1 = repl_match.get_target_node(self.node1)
        node1.assign_from(node0)

        # we need to prune columns in node1.str_
        assert isinstance(node0, SerializeFromObject)
        assert isinstance(node1, SerializeFromObject)
        raw_cols = node0.raw_cols
        attr2cols = {}
        for col in raw_cols:
            _, attr_str = col.split(' AS ')
            attr2cols[attr_str.strip()] = col.strip()

        pruned_cols = []
        for attr in reqs:
            attr_str = str(attr)
            assert attr_str in attr2cols, f"Required attr {attr_str} not found"
            pruned_cols.append(attr2cols[attr_str])
        s1 = '[' + ', '.join(pruned_cols) + ']'

        old_s = node1.serializer.value
        new_s = old_s[:old_s.find('[') + 1] + s1 + old_s[old_s.rfind(']'):]
        node1.serializer.init(new_s)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        node0 = target_match.get_target_node(self.node0)
        node1 = repl_match.get_target_node(self.node1)
        return [TransLink.mk_ch(node0, node1, 'serializer', 'serializer')]      # hard code param name


