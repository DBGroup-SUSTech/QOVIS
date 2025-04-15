from typing import Any, List, Callable, Optional


def find_last(lst: List[Any], pred: Callable[[Any], bool]) -> Optional[Any]:
    i = len(lst) - 1
    while i >= 0:
        item = lst[i]
        if pred(item):
            return item
    return None


def is_same_lst(lst1: List[Any], lst2: List[Any],
                key: Callable[[Any], Any] = lambda x: x) -> bool:
    if len(lst1) != len(lst2):
        return False
    for a, b in zip(lst1, lst2):
        if key(a) != key(b):
            return False
    return True
