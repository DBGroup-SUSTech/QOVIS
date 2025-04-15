class Constraint:
    def __init__(self):
        self.name = self.__class__.__name__

    def __str__(self):
        return self.name

# class AggrFuncEq(Constraint):
#     def __init__(self, id1: int, id2: int):
#         super().__init__()
#         self.id1 = id1
#         self.id2 = id2
#         self.node1: PlanPatternNode = None
#         self.node2: PlanPatternNode = None


# class IsUnique(SrcConstraint):
#     def __init__(self, rel: int):
#         super().__init__()
#         self.id = id_
#         self.node: PlanPatternNode = None
#
#     def init(self, src: PlanPatternNode):
#         self.node = self.find_by_id(self.id, src)
#
#     def check(self, match: PlanMatchNode) -> bool:
#         assert hasattr(match.node, "attrs")
#         assert hasattr(match.pattern, "attrs")
#         return len(match.node.attrs) == len(match.pattern.attrs)
