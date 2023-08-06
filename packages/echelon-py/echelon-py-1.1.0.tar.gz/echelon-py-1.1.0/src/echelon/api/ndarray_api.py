import numpy as np
from echelon.api.base import EchelonAnalysis
from echelon.oracle import NdarrayEchelonOracle
from echelon.scan_oracle import NdarrayBinomialScanOracle, NdarrayPoissonScanOracle

# Type hinting
from echelon.api.base import Result_EchelonAnalysis


class NdarrayEchelonAnalysis(EchelonAnalysis):
    def hotspots(self, result: Result_EchelonAnalysis, data=None, score=['poisson', 'binomial'][0]):
        """
        Parameters:
            data: tuple of data etc. The required data formats depend on the ``score`` parameter.

                  * If ``score == 'poisson'``,

                      * If ``data is None``, the original data is used.
                      * Otherwise, ``data`` should be an ``np.ndarray``, and it will be used to score the hot-spot-ness.

                  * If ``score == 'binomial'``,

                      * ``data`` should be a tuple ``(total_count_data, marked_count_data)``.
                        ``total_count_data`` should contain the total population of each index (the number of trials in the binomial distributions).
                        ``marked_count_data`` should contain the positive population of each index (the realized values of the binomial distributions).
        """
        if score == 'poisson':
            if data is None:
                scan_oracle = NdarrayPoissonScanOracle(self.data)
            else:
                assert isinstance(data, np.ndarray)
                scan_oracle = NdarrayPoissonScanOracle(data)
        elif score == 'binomial':
            total_count_data, marked_count_data = data
            scan_oracle = NdarrayBinomialScanOracle(total_count_data, marked_count_data)
        return super()._hotspots(result, scan_oracle)

    def __call__(self, data: np.ndarray, adjacency: np.ndarray) -> Result_EchelonAnalysis:
        """
        Parameters:
            data: 1-dimensional data of realized values.
            adjacency: ``len(data)``-sized square array of adjacency.

        Examples:
            >>> from echelon.test import _mock_1dim_data
            >>> h, W = _mock_1dim_data()
            >>> analyzer = NdarrayEchelonAnalysis()
            >>> result = analyzer(h, W)
            >>> result.peak_echelons
            [[16, 17, 15], [13], [6, 5, 7], [3], [23]]
            >>> result.foundation_echelons
            [[12, 14, 18, 19, 11, 10, 20], [2, 4, 8], [1, 9, 21], [0, 22, 24]]
        """
        self.data = data
        oracle = NdarrayEchelonOracle(data, adjacency)
        return self._run_analysis(oracle)


class OneDimEchelonAnalysis(NdarrayEchelonAnalysis):
    def __call__(self, data: np.ndarray) -> Result_EchelonAnalysis:
        """
        Parameters:
            data: 1-dimensional data of realized values.

        Examples:
            >>> from echelon.test import _mock_1dim_data, _visualize_echelons
            >>> h, _ = _mock_1dim_data()
            >>> analyzer = OneDimEchelonAnalysis()
            >>> result = analyzer(h)
            >>> result.peak_echelons
            [[16, 17, 15], [13], [6, 5, 7], [3], [23]]
            >>> result.foundation_echelons
            [[12, 14, 18, 19, 11, 10, 20], [2, 4, 8], [1, 9, 21], [0, 22, 24]]
            >>> print(h)
            [1 2 3 4 3 4 5 4 3 2 3 4 5 6 5 6 7 6 5 4 3 2 1 2 1]
            >>> print(_visualize_echelons(h.shape, result.peak_echelons, result.foundation_echelons))
            [9 8 7 4 7 3 3 3 7 8 6 6 6 2 6 1 1 1 6 6 6 8 9 5 9]
        """
        W = np.zeros((len(data),)*2, dtype='int8')
        W[np.eye(len(W), k=1, dtype='bool')] = 1
        W[np.eye(len(W), k=-1, dtype='bool')] = 1
        return super().__call__(data, W)


class TwoDimEchelonAnalysis(NdarrayEchelonAnalysis):
    """The standard API for two-dimensional matrix-shaped data.
    The API constructs the canonical adjacency matrix (i.e., the 4- or 8-neighborhood).
    """
    def __init__(self, adjacency_type='4'):
        super().__init__()
        if adjacency_type in ['4', '8']:
            self.adjacency_type = adjacency_type
        else:
            raise ValueError('Only 4 or 8 is allowed.')

    def _canonical_twodim_adjacency_4(self, n, m):
        """Construct the canonical adjacency matrix for two-dimensional data.
        The adjacency matrix is for the canonical 4-neighbors (up down left right;
        known as *von Neumann* neighborhood).

        Example:
            >>> print(TwoDimEchelonAnalysis()._canonical_twodim_adjacency_4(2, 2)[0].reshape(2, 2))
            [[0 1]
             [1 0]]
            >>> print(TwoDimEchelonAnalysis()._canonical_twodim_adjacency_4(3, 3)[4].reshape(3, 3))
            [[0 1 0]
             [1 0 1]
             [0 1 0]]
            >>> print(TwoDimEchelonAnalysis()._canonical_twodim_adjacency_4(3, 3)[5].reshape(3, 3))
            [[0 0 1]
             [0 1 0]
             [0 0 1]]
        """
        W = np.zeros((n * m,)*2, dtype='int8')

        for i in range(len(W)):
            for delta in [-m, m]:
                j = i + delta
                if (0 <= j) and (j <= len(W)-1):
                    W[i, j] = 1
            for delta in [-1, 1]:
                j = i + delta
                # If j does not move out to a different row
                if (0 <= j) and (j <= len(W)-1) and ((i // m) == (j // m)):
                    W[i, j] = 1
        return W

    def _canonical_twodim_adjacency_8(self, n, m):
        """Construct the canonical adjacency matrix for two-dimensional data.
        The adjacency matrix is for 8-neighbors (up down left right, and their combinations;
        known as *Moore* neighborhood).

        Example:
            >>> print(TwoDimEchelonAnalysis()._canonical_twodim_adjacency_8(2, 2)[0].reshape(2, 2))
            [[0 1]
             [1 1]]
            >>> print(TwoDimEchelonAnalysis()._canonical_twodim_adjacency_8(3, 3)[4].reshape(3, 3))
            [[1 1 1]
             [1 0 1]
             [1 1 1]]
            >>> print(TwoDimEchelonAnalysis()._canonical_twodim_adjacency_8(3, 3)[3].reshape(3, 3))
            [[1 1 0]
             [0 1 0]
             [1 1 0]]
        """
        W = np.zeros((n * m,)*2, dtype='int8')

        for i in range(len(W)):
            for delta in [-m-1, -m, -m+1]:
                j = i + delta
                if (0 <= j) and (j <= len(W)-1) and ((i // m) == (j // m + 1)):
                    # If j does not move out to a different row
                    W[i, j] = 1
            for delta in [m-1, m, m+1]:
                j = i + delta
                if (0 <= j) and (j <= len(W)-1) and ((i // m) == (j // m - 1)):
                    # If j does not move out to a different row
                    W[i, j] = 1
            for delta in [-1, 1]:
                j = i + delta
                if (0 <= j) and (j <= len(W)-1) and ((i // m) == (j // m)):
                    # If j does not move out to a different row
                    W[i, j] = 1
        return W

    def __call__(self, data: np.ndarray) -> Result_EchelonAnalysis:
        """
        Parameters:
            data: 2-dimensional data of realized values.

        Examples:
            >>> from echelon.test import _mock_2dim_data, _visualize_echelons
            >>> data, _ = _mock_2dim_data()
            >>> result = TwoDimEchelonAnalysis()(data)
            >>> result.peak_echelons
            [[14, 13, 8], [2], [11, 16], [24]]
            >>> result.foundation_echelons
            [[12], [19, 15, 9], [7, 20, 17, 18, 6, 22, 1, 23, 21, 3, 10, 4, 0, 5]]
            >>> print(data)
            [[ 2  8 24  5  3]
             [ 1 10 14 22 15]
             [ 4 21 19 23 25]
             [16 20 12 11 17]
             [13  6  9  7 18]]
            >>> print(_visualize_echelons(data.shape, result.peak_echelons, result.foundation_echelons))
            [[7 7 2 7 7]
             [7 7 7 1 6]
             [7 3 5 1 1]
             [6 3 7 7 6]
             [7 7 7 7 4]]

            >>> from echelon.test import _mock_2dim_data, _visualize_echelons
            >>> data, _ = _mock_2dim_data()
            >>> result = TwoDimEchelonAnalysis('8')(data)
            >>> result.peak_echelons
            [[14, 13], [2], [11, 16], [24]]
            >>> result.foundation_echelons
            [[8], [12], [19, 15, 9, 7, 20, 17, 18, 6, 22, 1, 23, 21, 3, 10, 4, 0, 5]]
            >>> print(data)
            [[ 2  8 24  5  3]
             [ 1 10 14 22 15]
             [ 4 21 19 23 25]
             [16 20 12 11 17]
             [13  6  9  7 18]]
            >>> print(_visualize_echelons(data.shape, result.peak_echelons, result.foundation_echelons))
            [[7 7 2 7 7]
             [7 7 7 5 7]
             [7 3 6 1 1]
             [7 3 7 7 7]
             [7 7 7 7 4]]
        """
        if self.adjacency_type == '4':
            W = self._canonical_twodim_adjacency_4(*data.shape)
        elif self.adjacency_type == '8':
            W = self._canonical_twodim_adjacency_8(*data.shape)

        return super().__call__(data.flatten(), W)
