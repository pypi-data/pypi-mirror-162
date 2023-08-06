from copy import copy, deepcopy
import numpy as np
from echelon.oracle import EchelonOracleBase
from echelon.algorithms.util import _flatten_lists, _lists_intersection

## Type hinting
from typing import Tuple, List, Iterable
from echelon.typing import EchelonsType


def find_foundation_echelons(oracle: EchelonOracleBase, peak_echelons: EchelonsType) -> EchelonsType:
    """Construct foundation echelons.

    Parameters:
        oracle: the oracle to query data.
        peak_echelons (:doc:`EchelonsType <echelon.typing>`): the peak echelons.

    Returns:
        :doc:`EchelonsType <echelon.typing>` : foundation_echelons

    Examples:
        >>> h = np.array([1, 2, 3, 4, 3, 4, 5, 4, 3, 2, 3, 4, 5, 6, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 1])
        >>> W = np.zeros((25, 25), dtype='int8')
        >>> W[np.eye(len(W), k=1, dtype='bool')] = 1
        >>> W[np.eye(len(W), k=-1, dtype='bool')] = 1
        >>> from echelon.oracle import NdarrayEchelonOracle
        >>> oracle = NdarrayEchelonOracle(h, W)
        >>> from echelon.algorithms.find_peak_echelons import find_peak_echelons
        >>> peak_echelons = find_peak_echelons(oracle)
        >>> find_foundation_echelons(oracle, peak_echelons)
        [[12, 14, 18, 19, 11, 10, 20], [2, 4, 8], [1, 9, 21], [0, 22, 24]]

    Notes:
        The algorithm is as follows.
        In this algorithm, we keep track of the list of *families*.
        Each "family" is a set of indices, and the initial set of families consist of the peak echelons.
        In the latter steps, the set of families grow.

        We define :math:`\mathrm{TangentFamily}(\mathrm{indices}) := \{F \in \mathrm{families} : F \cap \mathrm{nb}(\mathrm{indices}) ≠ \emptyset\}`.
        We also define :math:`\mathrm{DataMax}(\mathrm{indices}) := \max_{i \in \mathrm{indices}}\mathrm{Data}_i`
        and :math:`\mathrm{DataArgMax}(\mathrm{indices}) := \mathrm{argmax}_{i \in \mathrm{indices}}\mathrm{Data}_i`

            .. container:: algorithm-find-foundations
                :name: algorithm-find-foundations

                **Algorithm**

                #. Mark all indices in Peak Echelons as searched.
                #. We repeat the following until we run out of all unsearched indices.

                    #. Select one maximum point (foundation-top, :math:`t`) and the max value (:math:`v`) among the unsearched indices. That is, :math:`t \in \mathrm{DataArgMax}(\mathrm{unsearched})` and :math:`v = \mathrm{DataMax}(\mathrm{unsearched})`.
                    #. Initialize :math:`\mathrm{foundation}=\{t\}`.
                    #. Initialize the set of families :math:`\mathrm{families} = \{\mathrm{peak}'s\}`.
                    #. Initialize the temporary family :math:`\mathrm{tempFamily} = \mathrm{foundation}`.
                    #. We now run the following extension loop, consisting of two steps: **family extension** and **neighbor extension**.

                        #. **Family extension**.

                           #. Pop out the set of tangent families:

                               * :math:`\mathcal{F} = \mathrm{TangentFamily}(\mathrm{tempFamily})`.
                               * :math:`\mathrm{families} \gets \mathrm{families} \setminus \mathcal{F}`.

                           #. Merge the tangent families as :math:`\mathrm{tempFamily} \gets \mathrm{tempFamily} \cup (\cup \mathcal{F})`.

                        #. **Neighbor extension**.
                           We decide whether to extend the set of families to neighbors.

                           #. Get the set of neighbors :math:`N := \mathrm{nb}(\mathrm{tempFamily})`.
                           #. Find :math:`A := \mathrm{DataArgMax}(N)`.

                               * If the maximum value :math:`\mathrm{Data}_i` (:math:`i \in A`) equals :math`v`, then we regard :math:`A` to be as qualified as :math:`t` to be part of :math:`\mathrm{foundation}`,
                                 and therefore

                                   * Add :math:`A` to the foundation: :math:`\mathrm{foundation} \gets \mathrm{foundation} \cup (A \cap \mathrm{unsearched})`.
                                   * Add :math:`A` to the temporary family: :math:`\mathrm{tempFamily} \gets \mathrm{tempFamily} \cup (A \cap \mathrm{unsearched})`.
                                   * Mark :math:`A` as searched.

                               * If elements of :math:`A` contains no local minima, i.e., if :math:`\mathrm{DataMax}(A\cup \mathrm{tempFamily}) \geq \mathrm{DataMax}(\mathrm{nb}(A\cup \mathrm{tempFamily}))`, then

                                   * Add :math:`A` to the foundation: :math:`\mathrm{foundation} \gets \mathrm{foundation} \cup (A \cap \mathrm{unsearched})`.
                                   * Add :math:`A` to the temporary family: :math:`\mathrm{tempFamily} \gets \mathrm{tempFamily} \cup (A \cap \mathrm{unsearched})`.
                                   * Mark :math:`A` as searched.

                               * Otherwise, we halt the iterative loop, register :math:`\mathrm{foundation}` as a foundation echelon, add :math:`\mathrm{tempFamily}` to the set :math:`\mathrm{families}` as an element, and go back to the top of the loop

                #. After the loop is halted, we have the set of found :math:`\mathrm{foundation}`'s.

                The set of foundation echelons and the set of peak echelons are mutually exclusive and collectively exhaustive.
    """
    unsearched_inds = list(set(oracle.copy_indices())-set(_flatten_lists(peak_echelons)))
    families = deepcopy(peak_echelons)
    foundation_echelons = []

    while len(unsearched_inds):
        _current_echelon = []
        ## Select a single point among the unsearched maxima.
        _argmax_single, _initial_max = oracle.find_peaktop(unsearched_inds)
        _argmax = [_argmax_single]
        _current_echelon += _argmax
        _current_family = _argmax

        while True:
            ## Blocking statement
            if (not oracle.nb(_current_family)) or (not unsearched_inds):
                break
            ## Family extension
            _current_family, families = oracle.pop_extend_family(_current_family, families)
            ## Check neighbor argmax set
            _argmax, _max = oracle.max_nb(_current_family)
            # If the max value is the same as the original max, unconditionally accept them.
            if (_max == _initial_max):
                _current_family += _argmax
                _current_echelon += _lists_intersection(_argmax, unsearched_inds) # Foundation echelon contains only those which do not consist the peak echelons.
            # If none of the neighboring candidates is a local minimum, accept the candidates.
            elif (_max >= oracle.max_nb(_current_family + _argmax)[1]):
                _current_family += _argmax
                _current_echelon += _lists_intersection(_argmax, unsearched_inds) # Foundation echelon contains only those which do not consist the peak echelons.
            else:
                break

        families.append(_current_family)
        foundation_echelons.append(_current_echelon)
        unsearched_inds = list(set(unsearched_inds) - set(_current_echelon))
        if not unsearched_inds: # If all marked as searched
            break
    return foundation_echelons
