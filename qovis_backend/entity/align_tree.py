from typing import List

from entity.transform import Transform
from utils.tree_utils import to_tree_str


class AlignNode:
    def __init__(self, transform: Transform):
        self.transform: Transform = transform
        self.children: List[AlignNode] = []

    @staticmethod
    def build_with_children(transform: Transform, children: List['AlignNode']):
        node = AlignNode(transform)
        node.children = children
        return node

    def copy(self):
        node = AlignNode(self.transform)
        node.children = [c.copy() for c in self.children]
        return node

    def get_transforms(self) -> List[Transform]:
        ret = [self.transform]
        for child in self.children:
            ret.extend(child.get_transforms())
        return ret

    def to_tree_str(self):
        return to_tree_str(self, lambda x: x.children, lambda x: str(x.transform))

