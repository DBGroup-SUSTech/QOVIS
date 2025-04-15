from typing import Union, Optional

from trans.plan.param.attributes import Attributes
from trans.plan.param.base_param import BaseParam
from trans.plan.param.expression import Expression
from trans.plan.param.expressions import ExprsBuilder, Expressions
from trans.plan.param.predicate import Predicate
from trans.plan.plan_match import PlanMatch
from trans.plan.plan_node import PlanNode
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class ExprsEq(TransConstraint):
    def __init__(self, e0_or_builder: Union[Expressions, ExprsBuilder], e1: Expressions):
        super().__init__()
        self.e0: Optional[Expressions] = None
        self.e0_builder: Optional[Expressions] = None
        if isinstance(e0_or_builder, Expressions):
            self.e0 = e0_or_builder
        elif isinstance(e0_or_builder, ExprsBuilder):
            self.e0_builder = e0_or_builder
        else:
            raise ValueError(f"Invalid type: {type(e0_or_builder)}")
        self.e1 = e1

    def need_computation(self) -> bool:
        return self.e0_builder is not None

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        """
        target_match.target is the target plan tree.
        target_match.pattern is the src pattern of rule.
        repl_match.target is the repl plan tree.
        repl_match.pattern is the dst pattern of rule.
        """
        e1 = repl_match.get_target_param(self.e1)  # e1 is in some node in repl plan tree
        if self.need_computation():
            symbols = self.e0_builder.collect_symbols()
            sym2exprs_or_attrs = {}
            for s in symbols:
                if isinstance(s, Expressions):
                    # expressions can only belong to operator
                    sym2exprs_or_attrs[s] = target_match.get_target_param(s)
                else:
                    assert isinstance(s, Attributes)
                    # attributes can belong to operator or operator param
                    sym2exprs_or_attrs[s] = target_match.get_target_attrs(s)
            e0 = self.e0_builder.compute(sym2exprs_or_attrs)
        else:
            e0 = target_match.get_target_param(self.e0)     # e0 is in some node in target plan tree
        e1.init_from(e0)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        links = []

        e1 = repl_match.get_target_param(self.e1)
        node1 = e1.owner
        name1 = node1.get_param_name(e1)

        if self.need_computation():
            symbols = self.e0_builder.collect_symbols()
            for s in symbols:
                if isinstance(s, Expressions):
                    # expressions can only belong to operator
                    exprs0 = target_match.get_target_param(s)
                    node0 = exprs0.owner
                    name0 = node0.get_param_name(exprs0)
                    for idx0, expr0 in enumerate(exprs0.expr_list):
                        cand_exprs = []

                        # as_exprs will convert expr0.attr to exprs
                        # case 1: find expr0.attr in e1.expr_list
                        expr1 = e1.find_produced_expr(expr0.attr)       # find in produced expr as this is as_exprs
                        if expr1 is not None:
                            cand_exprs.append(expr1)
                        # collapse_to will merge expr0 and another expr to expr1
                        # another expr will be found in case 1
                        # case 2: find collapsed expr
                        for expr1 in e1.expr_list:
                            if all(expr1.attrs.includes(req) for req in expr0.attrs) and expr0.can_collapse_to(expr1):
                                cand_exprs.append(expr1)

                        cand_exprs = list(set(cand_exprs))
                        for expr1 in cand_exprs:
                            idx1 = e1.expr_list.index(expr1)
                            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))
                else:
                    assert isinstance(s, Attributes)
                    # attributes can belong to operator or operator param
                    # is surrounded by as_exprs(...), this converts A#1 (attr) -> A#1 as A#1 (expr)
                    attrs = target_match.get_target_attrs(s)
                    node0 = target_match.get_target_node_by_attrs(s)
                    name0 = node0.get_param_name(attrs)     # the name of attrs param OR its owner param in node0
                    # e.g., we bind pred.attrs to pred, so here the name0 is the name of pred in node0
                    if name0 is None:
                        print(f'Ignore {str(attrs)[:20]} in {str(node0)[:20]} as failed to find param name')
                        continue
                    links.extend(self._build_link_for_attr(attrs, node0, name0, e1, node1, name1))
        else:
            e0 = target_match.get_target_param(self.e0)
            node0 = e0.owner
            # links.append(TransLink.mk_eq(node0, node1))
            name0 = node0.get_param_name(e0)
            for idx in range(len(e0.expr_list)):
                links.append(TransLink.mk_ch(node0, node1, name0, name1, idx, idx))

        return links

    def _build_link_for_attr(self, attrs0: Attributes, node0: PlanNode, name0: str,
                             exprs1: Expressions, node1: PlanNode, name1: str) -> list[TransLink]:
        links = []

        if attrs0.belongs_to_op():
            raise NotImplementedError

        elif attrs0.belongs_to_exprs():
            # the attrs is called by "exprs.attrs" or "exprs.req_attrs"
            # so bind corresponding exprs0 to exprs in e1 by the required attrs of each item in exprs0
            exprs0: Expressions = attrs0.owner_exprs
            if attrs0 is exprs0.attrs:
                raise NotImplementedError
            else:
                assert attrs0 is exprs0.req_attrs
                for idx0, expr0 in enumerate(exprs0.expr_list):
                    req_attrs0 = expr0.attrs        # req attrs on this expr item
                    for idx1, expr1 in enumerate(exprs1.expr_list):
                        if req_attrs0.find(expr1.attr):
                            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))

        elif attrs0.belongs_to_pred():
            # the attrs is called by "pred.attrs"
            pred0: Predicate = attrs0.owner_pred
            # we visit each attr by different pred expression (each expression has a list "reqs")
            for idx0, expr_req_attrs in enumerate(pred0.reqs_list):
                for attr in expr_req_attrs.items:
                    idx1 = exprs1.index_by_produced_attr(attr)
                    if idx1 >= 0:
                        links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))

        elif attrs0.belongs_to_rel():
            # just ignore them as the rel will not show to the users
            pass

        elif attrs0.is_output():
            # e.g., join0.output
            # just ignore them as the output will not show to the users
            pass

        else:
            raise Exception(f"Unknown attribute kind: {attrs0.kind}")

        return links
