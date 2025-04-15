
class PredTreeNode:
    def __init__(self, expr: str):
        self.expr = expr
        self.left: 'PredTreeNode' = None
        self.right: 'PredTreeNode' = None

    def __repr__(self):
        if self.left is None and self.right is None:
            return f"{self.expr}"
        else:
            return f"({self.left} AND {self.right})"

    def __str__(self):
        return self.__repr__()


class PlanUtils:
    # @staticmethod
    # def build_expression_tree(expr_str: str) -> 'PredTreeNode':
    #     """
    #     Build an expression tree from a string.
    #     Example:
    #         Input: "(((A = B) OR (C = 1993)) AND (D >= 1))"
    #         Output:
    #             AND
    #             :- OR
    #             :  :- A = B
    #             :  +- C = 1993
    #             +- D >= 1
    #     Example2:
    #         Input: (((A = B) AND (C = 1993)) AND (((D >= 1) AND (E <= 3)) AND (F < 25)))
    #         Output:
    #             AND
    #             :- AND
    #             :  :- AND
    #             :  :  :- A = B
    #             :  :  +- C = 1993
    #             :  +- AND
    #             :     :- D >= 1
    #             :     +- E <= 3
    #             +- F < 25
    #     """
    #     def find_collector(expr: str) -> int:
    #         """
    #         Find the index of the collector "AND" or "OR".
    #         On the left, # of '(' should be equal to # of ')' + 1,
    #         and on the right, # of '(' + 1 should be equal to # of ')'.
    #         If the collector is not found, return -1.
    #         """
    #         # find the first ')'
    #         i = 0
    #         while i < len(expr):
    #             if expr[i] == '(':
    #                 i += 1
    #             elif expr[i] == ')':
    #                 return i
    #             else:
    #                 i += 1
    #         return -1

    @staticmethod
    def collect_and_expressions(expression: str) -> list[str]:
        tree = PlanUtils.parse_expression(expression)
        expr_list = []

        def fill_and(node):
            if node.left is not None and node.right is not None:
                fill_and(node.left)
                fill_and(node.right)
            else:
                expr = node.expr
                if expr.startswith('(') and expr.endswith(')'):
                    expr = expr[1:-1]
                expr_list.append(expr)

        fill_and(tree)
        return expr_list

    @staticmethod
    def parse_expression(expression: str) -> 'PredTreeNode':
        # find positions of all ANDs
        and_pos = []
        i = 0
        while i < len(expression):
            index = expression.find('AND', i)
            if index == -1:
                break
            and_pos.append(index)
            i = index + 3

        if len(and_pos) == 0:
            # no AND found
            return PredTreeNode(expression)

        # for each AND count the number of '(' and ')' on the left and right
        target = None
        for i in range(len(and_pos)):
            left = expression[:and_pos[i]]
            right = expression[and_pos[i] + 3:]
            left_count = left.count('(') - 1 - left.count(')')
            right_count = right.count('(') - right.count(')') + 1
            if left_count == 0 and right_count == 0:
                target = i
                break

        if target is None:
            raise Exception('Invalid expression:', expression)

        # build the tree
        node = PredTreeNode(expression[1:-1])
        node.left = PlanUtils.parse_expression(expression[1:and_pos[target]].strip())
        node.right = PlanUtils.parse_expression(expression[and_pos[target] + 3:-1].strip())

        return node


if __name__ == '__main__':
    res = PlanUtils.parse_expression("(((A = B) OR (C = 1993)) AND (D >= 1))")
    print(res)
    res = PlanUtils.collect_and_expressions("(((A = B) OR (C = 1993)) AND (D >= 1))")
    print(res)
    res = PlanUtils.parse_expression("(((A = B) AND (C = 1993)) AND (((D >= 1) AND (E <= 3)) AND (F < 25)))")
    print(res)
    res = PlanUtils.collect_and_expressions("(((A = B) AND (C = 1993)) AND (((D >= 1) AND (E <= 3)) AND (F < 25)))")
    print(res)
