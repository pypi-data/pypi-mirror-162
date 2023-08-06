"""
Usage visualization
=============

.. digraph:: G1

   Data [shape=oval, label="Data (pd.DataFrame)\n * Observed values \n * Adjacency information"];

   API [shape=box, color=blue, label="API's __call__() method"];
   Echelon [shape=oval, color=red, label="Echelon List Object"];
   Data -> API -> Echelon;

   API_hotspots [shape=box, color=blue, label="API's hotspots() method"];
   ScoreData [shape=oval, label="Auxiliary data \n for scoring \n (pd.DataFrame)"];
   Hotspots [shape=oval, label="Hotspot candidates"];
   ScoreData -> API_hotspots; Echelon -> API_hotspots -> Hotspots;

   API_cluster [shape=box, color=blue, label="API's cluster() method"];
   Clusters [shape=oval, label="Echelon clusters"];
   Echelon -> API_cluster -> Clusters;

   API_dendrogram [shape=box, color=blue, label="API's dendrogram() method"];
   Dendrogram [shape=oval, label="Dendrogram"];
   Echelon -> API_dendrogram -> Dendrogram;
"""
from echelon.api.base import EchelonAnalysis
from echelon.oracle import DataFrameEchelonOracle
from echelon.scan_oracle import DataFrameBinomialScanOracle, DataFramePoissonScanOracle

# Type hinting
from echelon.api.base import Result_EchelonAnalysis


class DataFrameEchelonAnalysis(EchelonAnalysis):
    """The standard API for the data (realized values and neighborhood information) stored in a DataFrame."""
    def hotspots(self, result: Result_EchelonAnalysis, data=None, score=['poisson', 'binomial'][0]):
        """
        Parameters:
            data: tuple of data etc. The required data formats depend on the ``score`` parameter.

                  * If ``score == 'poisson'``,

                      * If ``data is None``, the original data is used.
                      * Otherwise, ``data`` should be a tuple ``(df: pd.DataFrame, id_colname: str, id_count: str)``, and it will be used to score the hot-spot-ness.
                        ``df`` is the data. ``id_colname`` is the column name of the indices.
                        ``id_count`` indicates the column containing the count of each index (the realized values of the Poisson distributions).

                  * If ``score == 'binomial'``,

                      * ``data`` should be a tuple ``(df: pd.DataFrame, id_colname: str, total_count_colname: str, marked_count_colname: str)``, and it will be used to score the hot-spot-ness.
                        ``df`` is the data. ``id_colname`` is the column name of the indices.
                        ``total_count_colname`` indicates the column containing the total population of each index (the number of trials in the binomial distributions).
                        ``marked_count_colname`` indicates the column containing the positive population of each index (the realized values of the binomial distributions).
        """
        if score == 'poisson':
            if data is None:
                scan_oracle = DataFramePoissonScanOracle(self.df, self.id_colname, self.value_colname)
            else:
                df, id_colname, total_count_colname = data
                scan_oracle = DataFramePoissonScanOracle(df, id_colname, total_count_colname)
        elif score == 'binomial':
            df, id_colname, total_count_colname, marked_count_colname = data
            scan_oracle = DataFrameBinomialScanOracle(df, id_colname, total_count_colname, marked_count_colname)
        return super()._hotspots(result, scan_oracle)

    def __call__(self, df,
                 value_colname: str,
                 id_colname: str,
                 adjacency_colname: str) -> Result_EchelonAnalysis:
        """
        Parameters:
            df (pd.DataFrame): the dataframe containing the indices, observed values, and adjacency information.
            value_colname: column name of ``df`` corresponding to the observed values.
            id_colname: column name of ``df`` corresponding to the index values. The values in this column needs to be unique.
            adjacency_colname: column name of ``df`` corresponding to the adjacency information. The cells must contain lists of indices to which the record is adjacent.
        """
        self.df = df
        self.value_colname = value_colname
        self.id_colname = id_colname
        oracle = DataFrameEchelonOracle(df, value_colname, id_colname, adjacency_colname)
        return self._run_analysis(oracle)
