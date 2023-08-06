from copy import copy, deepcopy
import numpy as np
from echelon.oracle import EchelonOracleBase

## Type hinting
from typing import Tuple, List, Iterable
from echelon.typing import EchelonsType


def find_peak_echelons(oracle: EchelonOracleBase) -> EchelonsType:
    """
    Parameters:
        ``EchelonOracleBase`` oracle : the oracle to query the data.

    Returns:
        :doc:`EchelonsType <echelon.typing>` : peak_echelons

    Examples:
        >>> h = np.array([1, 2, 3, 4, 3, 4, 5, 4, 3, 2, 3, 4, 5, 6, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 1])
        >>> W = np.zeros((25, 25), dtype='int8')
        >>> W[np.eye(len(W), k=1, dtype='bool')] = 1
        >>> W[np.eye(len(W), k=-1, dtype='bool')] = 1
        >>> from echelon.oracle import NdarrayEchelonOracle
        >>> oracle = NdarrayEchelonOracle(h, W)
        >>> find_peak_echelons(oracle)
        [[16, 17, 15], [13], [6, 5, 7], [3], [23]]

    Notes:
        After finding the initial peaktop in each iteration,
        the algorithm takes the "set" of argmax indices,
        i.e., it considers the contour set in the neighborhood
        simultaneously as candidates.

            .. container:: algorithm-find-peaks
                :name: algorithm-find-peaks

                **Algorithm**

                #. We repeat the following until we run out of all unsearched indices.

                    #. Select one maximum point (summit, :math:`s`) and the max value (summit value, :math:`v`) among the unsearched indices. That is, :math:`s \in \mathrm{argmax}_{i \in \mathrm{unsearched}}\mathrm{Data}_i` and :math:`v = \mathrm{Data}_s`.
                    #. Initialize :math:`\mathrm{peak}=\{s\}`.
                    #. We now run the following extension loop:

                        We consider whether to extend :math:`\mathrm{peak}` to newly include
                        :math:`S := \mathrm{argmax}_{i \in N} \{\mathrm{Data}_i\}` where :math:`N := \mathrm{nb}(\mathrm{peak})`,
                        i.e., the maximizers among the neighbors of :math:`\mathrm{peak}`.
                        Here, argmax is understood as a set of indices.

                        * If :math:`S` contains no local minimum (i.e., if :math:`\mathrm{Data}_{i} \geq \max_{i \in \mathrm{nb}(N\cup S)}\mathrm{Data}_{i}` where :math:`i \in S`), then we extend the peak set: :math:`\mathrm{peak}\gets \mathrm{peak}\cup S`.
                        * Otherwise, we halt the extension loop, flag all elements of :math:`\mathrm{peak}` as searched, register :math:`\mathrm{peak}` as a found peak echelon, and go back to the top of the loop.

                #. After the loop is halted, we have the set of found :math:`\mathrm{peak}`'s (which may or may not jointly contain all indices. Those indices that do not belong to a peak echelon will belong to a foundation echelon later.).
    """
    indices = oracle.copy_indices()
    peak_echelons = []
    while len(indices):
        _current_echelon = []
        _removed = []

        ## Start from finding a single peak point among the remaining candidates.
        _argmax_single, _max = oracle.find_peaktop(indices)
        _argmax = [_argmax_single]

        ## Extend from the peak point to its neighbors until the search hits a local minimum.
        ## Handle ties simultaneously (i.e., argmax is a set, not a point).
        while _max > oracle.max_nb(_current_echelon + _argmax)[1]:
            ## If not local minimum, add to peak echelon
            ## and remove searched candidates.
            _current_echelon += _argmax
            _removed += _argmax
            ## And continue to next round
            _argmax, _max = oracle.max_nb(_current_echelon)
        _removed += _argmax # Remove searched candidates
        if len(_current_echelon):
            peak_echelons.append(_current_echelon)
        indices = list(set(indices) - set(_current_echelon) - set(_removed))
    return peak_echelons
