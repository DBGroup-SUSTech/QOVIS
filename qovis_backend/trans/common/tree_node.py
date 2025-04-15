from typing import Callable, Optional

from utils.tree_utils import to_tree_str


class TreeNode(object):
    def __init__(self):
        self.children: [TreeNode] = []

    def find(self, f: Callable[['TreeNode'], bool]) -> Optional['TreeNode']:
        def find_recursively(node: TreeNode) -> Optional[TreeNode]:
            if f(node):
                return node
            for c in node.children:
                found = find_recursively(c)
                if found:
                    return found
            return None
        return find_recursively(self)

    def find_by_id(self, id_: int) -> Optional['TreeNode']:
        return self.find(lambda n: n.id == id_)

    def to_tree_str(self, to_str=lambda v: str(v)):
        return to_tree_str(self, lambda v: v.children, to_str)

    def collect_all(self):
        yield self
        for c in self.children:
            if c is None:
                continue
            yield from c.collect_all()
