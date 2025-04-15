from typing import List


def to_tree_str(node, get_children=lambda x: x.children, to_str=lambda x: str(x)) -> str:
    """
    Print the tree structure of the alignment tree.
    """
    return '\n'.join(_to_str_helper(node, get_children, to_str))


def _to_str_helper(node, get_children, to_str, prefix='', is_root=True, is_last=True) -> List[str]:
    ret = []
    one_line_str = prefix + ('' if is_root else ('└─ ' if is_last else '├─ ')) + to_str(node)
    ret.append(one_line_str)

    if node is None:
        return ret
    children = get_children(node)

    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        child_prefix = prefix + ('' if is_root else ('   ' if is_last else '│  '))
        child_lines = _to_str_helper(child, get_children, to_str, child_prefix, False, is_last_child)
        ret.extend(child_lines)

    return ret
