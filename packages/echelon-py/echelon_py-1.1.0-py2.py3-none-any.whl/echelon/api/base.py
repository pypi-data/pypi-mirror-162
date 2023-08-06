from dataclasses import dataclass
import pandas as pd
from echelon.algorithms import (find_peak_echelons,
                                find_foundation_echelons,
                                find_echelon_clusters,
                                find_echelon_hierarchy,
                                find_echelon_hotspots)
from echelon.oracle import EchelonOracleBase
from echelon.scan_oracle import ScanOracleBase
## Type hinting
from typing import Tuple, List, Union, Any, Dict, NewType
from anytree import Node
from echelon.typing import EchelonsType


Result_EchelonCluster = NewType('Result_EchelonCluster', pd.DataFrame)
"""The result of echelon cluster analysis."""


Result_EchelonHotspot = NewType('Result_EchelonHotspot', pd.DataFrame)
"""The result of echelon scan for hot-spot detection."""


@dataclass
class Result_EchelonAnalysis:
    """Dataclass for keeping the results of echelon analysis.

    Parameters:
        peak_echelons (:doc:`EchelonsType <echelon.typing>`): list of peak echelons.
        foundation_echelons (:doc:`EchelonsType <echelon.typing>`): list of foundation echelons.
        hierarchy_tree: root node (``anytree.Node``) of the hierarchy tree of the echelons.
        oracle: the oracle that is internally constructed during the instantiation of the analysis. Mainly for debugging purposes.
    """
    peak_echelons: EchelonsType
    foundation_echelons: EchelonsType
    hierarchy_tree: Node
    oracle: EchelonOracleBase

    @property
    def echelons(self) -> EchelonsType:
        """
        Returns:
            :doc:`EchelonsType <echelon.typing>` : echelons
        """
        return self.peak_echelons + self.foundation_echelons


class EchelonAnalysis:
    def cluster(self, result: Result_EchelonAnalysis) -> Result_EchelonCluster:
        """
        Examples:
            >>> from echelon.test import _mock_1dim_data
            >>> h, W = _mock_1dim_data()
            >>> analyzer = EchelonAnalysis()
            >>> from echelon.oracle import NdarrayEchelonOracle
            >>> oracle = NdarrayEchelonOracle(h, W)
            >>> result = analyzer._run_analysis(oracle)
            >>> analyzer.cluster(result)
              representatives                               indices
            0            [16]  [16, 17, 15, 14, 18, 19, 20, 21, 22]
            1            [13]               [13, 12, 14, 11, 10, 9]
            2             [6]                    [6, 5, 7, 4, 8, 9]
            3             [3]                       [3, 2, 4, 1, 0]
            4            [23]                          [23, 22, 24]
        """
        clusters = find_echelon_clusters(result.peak_echelons, result.foundation_echelons, result.oracle)
        echelon_clusters = []
        for cluster in clusters:
            _argmax, _ = result.oracle.max_indices(cluster)
            echelon_clusters.append((_argmax, cluster))
        return pd.DataFrame(echelon_clusters, columns =['representatives', 'indices'])

    def dendrogram(self, result: Result_EchelonAnalysis,
                   plot_config_dict: dict=dict(num_linespace = 1)) -> str:
        """Draw a simple dendrogram-like figure of the echelon hierarchy.

        Parameters:
            result : the result object of the echelon construction.
            plot_config_dict : the dictionary to configure the visualization.
        """
        from anytree import RenderTree

        root = result.hierarchy_tree
        echelons = result.echelons

        def _default_echelon_to_str(echelon_id, _echelon, _max_idx, value, plot_config_dict):
            """Default function to convert echelon information to a string."""
            idx_map = plot_config_dict.get('idx_map', str)
            representatives = ",".join(map(idx_map, _max_idx))
            echelon_contents = ', '.join(map(idx_map, reversed(_echelon)))
            return f'E{echelon_id+1}({representatives}): [{echelon_contents}]\n (max: {value})' + '\n' * plot_config_dict.get('num_linespace', 0)

        def echelon_to_label(echelon_id):
            _echelon = echelons[echelon_id]
            _max_idx, value = result.oracle.max_indices(_echelon)
            _echelon_to_str = plot_config_dict.get('_echelon_to_str', _default_echelon_to_str)
            return _echelon_to_str(echelon_id, _echelon, _max_idx, value, plot_config_dict)

        return RenderTree(root).by_attr(lambda node: echelon_to_label(node.name))

    def _hotspots(self, result: Result_EchelonAnalysis, scan_oracle: ScanOracleBase) -> Result_EchelonHotspot:
        hotspots = find_echelon_hotspots(scan_oracle,
                                            result.hierarchy_tree,
                                            result.echelons,
                                            result.oracle)
        return hotspots

    def _run_analysis(self, oracle: EchelonOracleBase) -> Result_EchelonAnalysis:
        peak_echelons = find_peak_echelons(oracle)
        foundation_echelons = find_foundation_echelons(oracle, peak_echelons)
        hierarchy = find_echelon_hierarchy(peak_echelons, foundation_echelons, oracle)
        return Result_EchelonAnalysis(
            peak_echelons=peak_echelons,
            foundation_echelons=foundation_echelons,
            hierarchy_tree = hierarchy,
            oracle=oracle
        )
