from enum import Enum
from typing import List, Dict

from entity.plan import Plan
from utils.id_counter import IdCounter


class ProcType(Enum):
    Root = 'root'
    Phase = 'phase'
    Batch = 'batch'
    Rule = 'rule'
    Other = 'other'
    Group = 'group'
    Unknown = 'unknown'


class TraceNode:
    def __init__(self, id: int, name: str = '', type_: str = 'other', start_idx: int = -1, end_idx: int = -1):
        self.id = id
        self.name: str = name
        self.type: str = type_
        self.start_idx: int = start_idx
        self.end_idx: int = end_idx

        self.start_time: str = ''
        self.end_time: str = ''

        self.events: List[Dict] = []
        self.children: List[TraceNode] = []

        # temp variables for parsing
        self.start_plan: Plan = None
        self.end_plan: Plan = None
        self.is_partial = False

    def update(self, name: str, type_: str) -> 'TraceNode':
        self.name = name
        self.type = type_
        return self

    def __repr__(self):
        return f"{self.name}#{self.id}(type={self.type}, start={self.start_idx}, end={self.end_idx})"

    def dump(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'startIdx': self.start_idx,
            'endIdx': self.end_idx,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'events': self.events,
            'children': [c.dump() for c in self.children],
        }

    @staticmethod
    def load(data):
        node = TraceNode(
            id=data['id'],
            name=data['name'],
            type_=data['type'],
            start_idx=data['startIdx'],
            end_idx=data['endIdx'],
        )
        node.start_time = data['startTime']
        node.end_time = data['endTime']
        node.events = data['events']
        node.children = [TraceNode.load(c) for c in data['children']]
        return node


class TraceTree:
    def __init__(self):
        self._id_counter = IdCounter()
        self.root: TraceNode = TraceNode(self.get_id())

    def get_id(self) -> int:
        return self._id_counter.get()

    def find_step_plan_indices(self, step_name: str, index: int = 0) -> tuple[int, int]:
        cur_idx = 0

        def find_step(node: TraceNode):
            nonlocal cur_idx
            if node.name == step_name:
                if cur_idx == index:
                    return node
                cur_idx += 1
            for child in node.children:
                result = find_step(child)
                if result:
                    return result
            return None

        step = find_step(self.root)

        if step is None:
            return -1, -1
        return step.start_idx, step.end_idx

    def find_minimum_step_by_start_idx(self, start_idx: int) -> TraceNode:
        def find(node: TraceNode):
            if node.start_idx == start_idx and len(node.children) == 0:
                assert node.end_idx == start_idx + 1
                return node
            for child in node.children:
                result = find(child)
                if result:
                    return result
            return None

        return find(self.root)

    def dump(self):
        return self.root.dump()

    @staticmethod
    def load(data):
        tree = TraceTree()
        tree.root = TraceNode.load(data)
        return tree
