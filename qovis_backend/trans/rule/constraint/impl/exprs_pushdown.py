from trans.plan.param.expression import Expression
from trans.plan.param.expressions import Expressions
from trans.plan.plan_match import PlanMatch
from trans.rule.constraint.trans_constraint import TransConstraint
from trans.rule.trans_link import TransLink


class ExprsPushdown(TransConstraint):
    def __init__(self, e0: Expressions, e1: Expressions, e2: Expressions, e3: Expressions):
        super().__init__()
        self.e0 = e0        # upper one
        self.e1 = e1        # below one
        self.e2 = e2
        self.e3 = e3

    def apply(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[PlanMatch]:
        e0 = target_match.get_target_param(self.e0)
        e1 = target_match.get_target_param(self.e1)
        e2 = repl_match.get_target_param(self.e2)
        e3 = repl_match.get_target_param(self.e3)

        e2_items = []
        e3_items = []
        processed = set()   # processed expr b in e1

        for a in e0.expr_list:
            if (a.kind == Expression.Kind.FUNCTION or a.kind == Expression.Kind.OTHER) \
                    and len(a.attrs) == 1:
                # pushdown expression
                used_attr = a.attrs[0]
                bs = e1.find_usage_expr(used_attr)

                if len(bs) == 1:
                    b = bs[0]

                    if b.kind == Expression.Kind.ATTR:
                        # a = {expr(b.attr) AS a.attr}  ->  {_tmp AS a.attr}
                        # b = {b.attr}                  ->  {expr(b.attr) AS _tmp}
                        tmp_attr_str = f"_tmp_{b.attr.name}#-{b.attr.id}"
                        expr_str = a.expr  # i.e., expr(b.attr)
                        a2 = Expression(f"{tmp_attr_str} AS {a.attr}")
                        b2 = Expression(f"{expr_str} AS {tmp_attr_str}")
                        e2_items.append(a2)
                        e3_items.append(b2)
                        processed.add(b)
                        continue

                    if b.kind == Expression.Kind.ATTR_RENAME:
                        # a = {expr(b.attr) AS a.attr}  ->  {_tmp AS a.attr}
                        # b = {b.attrs[0] AS b.attr}    ->  {expr(b.attrs[0]) AS _tmp}
                        tmp_attr_str = f"_tmp_{b.attr.name}#-{b.attr.id}"
                        expr_str = a.expr.replace(str(b.attr), b.attrs[0])
                        a2 = Expression(f"{tmp_attr_str} AS {a.attr}")
                        b2 = Expression(f"{expr_str} AS {tmp_attr_str}")
                        e2_items.append(a2)
                        e3_items.append(b2)
                        processed.add(b)
                        continue

            e2_items.append(a.copy())

        for b in e1.expr_list:
            if b in processed:
                continue
            e3_items.append(b.copy())

        e2.init_from_expr_list(e2_items)
        e3.init_from_expr_list(e3_items)

        return [repl_match]

    def get_links(self, target_match: PlanMatch, repl_match: PlanMatch) -> list[TransLink]:
        node0 = target_match.get_target_node_by_param(self.e0)
        node1 = target_match.get_target_node_by_param(self.e1)
        node2 = repl_match.get_target_node_by_param(self.e2)
        node3 = repl_match.get_target_node_by_param(self.e3)

        p0 = target_match.get_target_param(self.e0)
        p1 = target_match.get_target_param(self.e1)
        p2 = repl_match.get_target_param(self.e2)
        p3 = repl_match.get_target_param(self.e3)

        name0 = node0.get_param_name(p0)
        name1 = node1.get_param_name(p1)
        name2 = node2.get_param_name(p2)
        name3 = node3.get_param_name(p3)

        links = []

        for idx0, expr in enumerate(p0.expr_list):
            idx1 = p1.expr_list.index(expr)
            links.append(TransLink.mk_ch(node0, node1, name0, name1, idx0, idx1))
        for idx2, expr in enumerate(p2.expr_list):
            idx3 = p3.expr_list.index(expr)
            links.append(TransLink.mk_ch(node2, node3, name2, name3, idx2, idx3))

        return links
