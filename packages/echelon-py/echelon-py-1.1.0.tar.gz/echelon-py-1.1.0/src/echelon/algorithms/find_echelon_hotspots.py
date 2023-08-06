from anytree import PreOrderIter
import pandas as pd

# Type hinting
from typing import List, Tuple, Any
from anytree import Node
from echelon.oracle import EchelonOracleBase
from echelon.scan_oracle import ScanOracleBase, EchelonScanStop


def find_echelon_hotspots(scan_oracle: ScanOracleBase, tree_root: Node, echelons, original_oracle: EchelonOracleBase) -> pd.DataFrame:
    """

    Notes:
        This method constructs the candidates of the hot spot :math:`Z` using the information from the echelon hierarchy.
        *Algorithm*

            * Let :math:`\{E_k\}_{k=1}^K` be the echelons sorted (in descending order) based on the maximum observation values of the indices in the echelon (used for constructing the echelons).
            * Let :math:`E_k = \{e_{k,j}\}_{j=1}^{n_k}` be the indices in each echelon sorted (in descending order) based on the original observation values.
            * We define the hot-spot candidates :math:`Z_{kj} := (\cup_{k' \in \mathrm{descendants}(k)} E_{k'}) \cup \{e_{k,1}, \ldots, e_{k,j}\}.` That is, we accumulate the elements in :math:`E_k` up to the index :math:`j`, as well as all of its descendants.
            * We score the candidates based on the binomial scan score.
    """
    ## Order echelons by the original oracle values.
    ## Traverse echelons (each node corresponds to an echelon)
    echelon_nodes = []
    for node in PreOrderIter(tree_root):
        _orig_score = original_oracle.max_indices(echelons[node.name])[1]
        echelon_nodes.append((_orig_score, node))

    from copy import copy
    _out = []
    ## From top echelons to the root echelons.
    ## Order is determined by the representative observation values.
    for _, node in reversed(sorted(echelon_nodes, key=lambda a: a[0])):
        Z = sum([echelons[n.name] for n in node.descendants], [])
        for ind in echelons[node.name]:
            Z.append(ind)
            try:
                score, record_values = scan_oracle.score(Z)
            except EchelonScanStop as e:
                break

            _out.append({
                'spot': copy(Z),
                'score': score,
                **record_values
            })
    return pd.DataFrame(_out).sort_values('score', ascending=False)
