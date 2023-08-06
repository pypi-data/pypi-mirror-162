## Type hinting
from typing import Tuple, List, Iterable


def _lists_intersection(list1, list2) -> list:
    return list(set(list1).intersection(list2))

def _flatten_lists(lists: Iterable[list]) -> list:
    return sum(lists, [])
