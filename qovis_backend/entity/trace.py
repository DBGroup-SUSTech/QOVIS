from typing import List

from entity.plan import Plan
from entity.trace_tree import TraceTree, TraceNode
from entity.transform import Transform


class Trace:
    def __init__(self):
        self.name: str = ''
        self.plans: List[Plan] = []
        self.transform_lists: List[List[Transform]] = []
        self.costs: List[float] = []
        self.trace_tree: TraceTree = TraceTree()

    def dump(self):
        return {
            'name': self.name,
            'plans': [p.dump() for p in self.plans],
            'transformLists': [[t.dump() for t in lst] for lst in self.transform_lists],
            'costs': self.costs,
            'traceTree': self.trace_tree.dump(),
        }

    @staticmethod
    def load(obj):
        trace = Trace()
        trace.name = obj['name']
        trace.plans = [Plan.load(p) for p in obj['plans']]
        if 'transformLists' in obj:
            trace.transform_lists = [[Transform.load(t) for t in s] for s in obj['transformLists']]
        if 'costs' in obj:
            trace.costs = obj['costs']
        trace.trace_tree = TraceTree.load(obj['traceTree'])
        return trace
