from copy import copy, deepcopy
import numpy as np
from anytree import Node
from echelon.oracle import EchelonOracleBase

## Type hinting
from typing import Tuple, List, Iterable, Any, Callable
from echelon.typing import EchelonsType


def find_echelon_hierarchy(peak_echelons: EchelonsType, foundation_echelons: EchelonsType, oracle) -> Node:
    """
    Parameters:
        peak_echelons (:doc:`EchelonsType <echelon.typing>`)
        foundation_echelons (:doc:`EchelonsType <echelon.typing>`)

    Returns:
        Root node of the hierarchy.

    Notes:
        **Algorithm**

        The algorithm is recursive.

        #. Given a list of echelon indices, find the maximum index value, and consider it the root node :math:`R`.

            #. If the rest of the indices is empty, return.
            #. Otherwise, split the rest of the indices into connected components (where echelons are considered to be adjacent when they have adjacent elements).

                * Parse each connected component by calling this procedure recursively.
                * For each of the connected components, we obtain its root node :math:`r`.
                  Attach :math:`r` to :math:`R` as its child.

    Examples:
        >>> from echelon.test import AdjacencyOracleMockup, _visualize_echelon_hierarchy
        >>> import string
        >>> oracle = AdjacencyOracleMockup(list(string.ascii_uppercase)[:25])
        >>> peak_echelons = [['Q', 'P', 'R'], ['N'], ['G', 'F', 'H'], ['D'], ['X']]
        >>> foundation_echelons = [['M', 'O', 'S', 'L', 'T', 'K', 'U'], ['C', 'E', 'I'], ['B', 'J', 'V'], ['A', 'W', 'Y']]
        >>> _visualize_echelon_hierarchy(find_echelon_hierarchy(peak_echelons, foundation_echelons, oracle))
        9
        ├── 8
        │   ├── 7
        │   │   ├── 4
        │   │   └── 3
        │   └── 6
        │       ├── 2
        │       └── 1
        └── 5
    """
    if not foundation_echelons:
        return list(reversed(range(len(peak_echelons))))

    echelons = peak_echelons + foundation_echelons
    echelon_ids = list(reversed(range(len(peak_echelons) + len(foundation_echelons))))

    class _EchelonSetOracle:
        """Utility class to simplify access."""
        def __init__(self, echelons, oracle: EchelonOracleBase):
            self.echelons = echelons
            self.oracle = oracle

        def is_connected(self, echelon_id1: int, echelon_id2: int) -> bool:
            return self.oracle.is_neighbor(self.echelons[echelon_id1], self.echelons[echelon_id2])

        def __call__(self, echelon_id1: int, echelon_id2: int) -> bool:
            return self.is_connected(echelon_id1, echelon_id2)

    echelon_oracle = _EchelonSetOracle(echelons, oracle)

    ## Prepare adjacency matrix. Used later to find connected components.
    # Alternative implementation: https://stackoverflow.com/questions/42251308/python-connected-components-edges-list
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.connected_components.html
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html
    from scipy.sparse import csr_matrix
    adj = csr_matrix((len(echelons),)*2, dtype='bool')
    import itertools
    for i, j in itertools.combinations(range(len(echelons)), 2):
        if echelon_oracle.is_connected(i, j):
            adj[i,j] = 1
            adj[j,i] = 1
    from scipy.sparse.csgraph import connected_components
    def _split_connected_indices(indices):
        """Split (subset of) echelon indices into connected components
        based on the oracle's adjacency information.
        """
        n, label = connected_components(adj[indices][:,indices])
        out = [[] for _ in range(n)]
        for l, ind in zip(label, indices):
            out[l].append(ind)
        return out

    ## Parse echelon indices.
    def _build_tree(ll, parent):
        """Parse the echelon indices into a tree.
        Recursive function.
        """
        if not len(ll):
            return
        max_id = ll.pop(ll.index(max(ll)))
        _root = Node(max_id, parent=parent)

        if not len(ll):
            return

        ## Split into connected components
        for component in _split_connected_indices(ll):
            assert len(component)
            ## Process each connected component
            _build_tree(component, _root)
        return _root

    ## Run recursive process.
    root = _build_tree(echelon_ids, None)
    return root
