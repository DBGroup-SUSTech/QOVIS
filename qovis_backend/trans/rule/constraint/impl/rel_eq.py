from typing import Union, Optional

from trans.plan.operator.input_like import InputLike
from trans.plan.param.attributes import Attributes
from trans.plan.param.expressions import Expressions
from trans.plan.param.relation import Relation, RelBuilder
from trans.plan.plan_match import PlanMatch
from trans.plan.plan_node import PlanNode
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class RelEq(TransConstraint):
    def __init__(self, rel0_or_builder: Union[Relation, RelBuilder], rel1: Relation):
        super().__init__()
        self.rel0: Optional[Relation] = None
        self.rel0_builder: Optional[Relation] = None
        if isinstance(rel0_or_builder, Relation):
            self.rel0 = rel0_or_builder
        elif isinstance(rel0_or_builder, RelBuilder):
            self.rel0_builder = rel0_or_builder
        else:
            raise ValueError(f"Invalid type: {type(rel0_or_builder)}")
        self.rel1 = rel1

    def need_computation(self) -> bool:
        return self.rel0_builder is not None

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        rel1 = repl_match.get_target_param(self.rel1)
        node1 = rel1.owner
        if not node1.is_param_required(rel1):
            return [repl_match]

        if self.need_computation():
            symbols = self.rel0_builder.collect_symbols()
            sym2exprs_or_attrs = {}
            for s in symbols:
                if isinstance(s, Expressions):
                    # expression can only belong to operator
                    sym2exprs_or_attrs[s] = target_match.get_target_param(s)
                else:
                    assert isinstance(s, Attributes)
                    # attributes can belong to operator or operator param
                    sym2exprs_or_attrs[s] = target_match.get_target_attrs(s)
            rel0 = self.rel0_builder.compute(sym2exprs_or_attrs)
        else:
            rel0 = target_match.get_target_param(self.rel0)

        rel1.init_from(rel0)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        rel1 = repl_match.get_target_param(self.rel1)
        node1 = repl_match.get_target_node_by_param(self.rel1)

        if not node1.is_param_required(rel1):
            return []

        links = []
        name1 = node1.get_param_name(rel1)

        if self.need_computation():
            symbols = self.rel0_builder.collect_symbols()
            for s in symbols:
                if isinstance(s, Expressions):
                    # expressions can only belong to operator
                    exprs0 = target_match.get_target_param(s)
                    node0 = exprs0.owner
                    name0 = node0.get_param_name(exprs0)
                    # exprs0 -> rel1
                    # rel0
                    for idx0, expr0 in enumerate(exprs0.expr_list):
                        if rel1.attrs.includes(expr0.attr):
                            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0))

                else:
                    assert isinstance(s, Attributes)
                    # attributes can belong to operator or operator param
                    attrs = target_match.get_target_attrs(s)
                    node0 = target_match.get_target_node_by_attrs(s)
                    name0 = node0.get_param_name(attrs)     # the name of attrs param OR its owner param in node0
                    if name0 is None:
                        print(f'Ignore {str(attrs)[:30]} in {str(node0)[:30]} as failed to find param name')
                        continue
                    links.extend(self._build_link_for_attr(attrs, node0, name0, rel1, node1, name1))
        else:
            rel0 = target_match.get_target_param(self.rel0)
            node0 = rel0.owner
            name0 = node0.get_param_name(rel0)
            links.append(TransLink.mk_ch(node0, node1, name0, name1))

        return links

    def _build_link_for_attr(self, attrs0: Attributes, node0: PlanNode, name0: str,
                             rel1: Relation, node1: PlanNode, name1: str) -> list[TransLink]:
        links = []

        if attrs0.belongs_to_op():
            raise NotImplementedError

        elif attrs0.belongs_to_exprs():
            raise NotImplementedError

        elif attrs0.belongs_to_pred():
            raise NotImplementedError

        elif attrs0.belongs_to_rel():
            links.append(TransLink.mk_ch(node0, node1, name0, name1))       # relation does not have param index

        elif attrs0.is_output():
            # e.g., join0.output
            # just ignore them as the output will not show to the users
            pass

        else:
            raise Exception(f"Unknown attribute kind: {attrs0.kind}")

        return links
