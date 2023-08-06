from copy import copy, deepcopy
import numpy as np
from echelon.oracle import EchelonOracleBase
from echelon.algorithms.util import _lists_intersection

## Type hinting
from typing import Tuple, List, Iterable
from echelon.typing import EchelonsType


def find_echelon_clusters(peak_echelons: EchelonsType, foundation_echelons: EchelonsType, oracle):
    """Find the Echelon Clusters.

    Parameters:
        peak_echelons (:doc:`EchelonsType <echelon.typing>`)
        foundation_echelons (:doc:`EchelonsType <echelon.typing>`)

    Examples:
        >>> h = np.array([1, 2, 3, 4, 3, 4, 5, 4, 3, 2, 3, 4, 5, 6, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 1])
        >>> W = np.zeros((25, 25), dtype='int8')
        >>> W[np.eye(len(W), k=1, dtype='bool')] = 1
        >>> W[np.eye(len(W), k=-1, dtype='bool')] = 1
        >>> from echelon.oracle import NdarrayEchelonOracle
        >>> from echelon.algorithms import find_peak_echelons, find_foundation_echelons
        >>> oracle = NdarrayEchelonOracle(h, W)
        >>> peak_echelons = find_peak_echelons(oracle)
        >>> foundation_echelons = find_foundation_echelons(oracle, peak_echelons)
        >>> find_echelon_clusters(peak_echelons, foundation_echelons, oracle)
        [[16, 17, 15, 14, 18, 19, 20, 21, 22], [13, 12, 14, 11, 10, 9], [6, 5, 7, 4, 8, 9], [3, 2, 4, 1, 0], [23, 22, 24]]
    """
    zones = deepcopy(peak_echelons)
    for echelon in foundation_echelons:
        for element in echelon:
            for i, zone in enumerate(zones):
                if _lists_intersection(oracle.nb([element]), zone):
                    zones[i].append(element)
    return zones
