"""This module contains the oracles used to run the echelon scan for hot-spot detection.
The oracles provide the scores for the hot-spot detection.
"""
import numpy as np

# Type hinting
from typing import List, Tuple, Any
from abc import ABCMeta, abstractmethod


class EchelonScanStop(Exception):
    pass


class ScanOracleBase(metaclass=ABCMeta):
    @abstractmethod
    def score(self, indices: List[int]) -> Tuple[Any, dict]:
        pass


class ApproxBinomialScanOracleBase(ScanOracleBase):
    """
    Notes:
        Consider :math:`K` regions and let us denote :math:`[K] := \{1, 2, \ldots, K\}`.
        For each region :math:`k \in [K]`, assume :math:`c_k \sim \mathrm{Bi}(\\\theta_k, n_k)`.

        Consider a region :math:`Z \subset [K]`. We assign a score :math:`s` that indicates how "hot-spot-ish" the region :math:`Z` is.

        Let us assume that :math:`(\\theta_k)_{k\in Z}` and :math:`(\\theta_k)_{k\in Z^\mathrm{c}}` are constants, :math:`\\theta_Z` and :math:`\\theta_{Z^\mathrm{c}}`, respectively.
        We compare the maximum likelihood under :math:`\\theta_Z = \\theta_{Z^\mathrm{c}}` and :math:`\\theta_Z > \\theta_{Z^\mathrm{c}}`.
        Denote :math:`c_Z := \sum_{k \in Z} c_k`, :math:`n_Z := \sum_{k \in Z} n_k`, :math:`n_{Z^{\mathrm{c}}} := \sum_{k \in Z^{\mathrm{c}}} n_k`, and :math:`n_{Z^{\mathrm{c}}} := \sum_{k \in Z^{\mathrm{c}}} n_k`.

        Now, by the reproductive property, :math:`c_Z \sim \mathrm{Bi}(\\theta_Z, n_Z)` where :math:`\\theta_Z = \sum_{k \in Z} \\theta_k`.
        Similarly for :math:`c_{Z^\mathrm{c}}`.
        Since the maximum likelihood of :math:`c \sim \mathrm{Bi}(\\theta, n)` is :math:`\mathrm{Bi}(\\frac{c}{n}, n)(c)` (by abuse of notation, we denote the density of a distribution by the name of the distribution).

        Now, when :math:`n >> c`, we have :math:`\mathrm{Bi}(\\theta, n)(c) \simeq (\\theta)^c`.

        With this approximation, the score for the case that :math:`\\theta_Z > \\theta_{Z^\mathrm{c}}` is
        :math:`\log (\\frac{c_Z}{n_Z})^{c_Z} + \log (\\frac{c_{Z^\mathrm{c}}}{n_{Z^\mathrm{c}}})^{c_{Z^\mathrm{c}}}`.

        Similarly, the score for the case that :math:`\\theta_Z = \\theta_{Z^\mathrm{c}}` is :math:`\log (\\frac{c_{[K]}}{n_{[K]}})^{c_{[K]}}`.

        Thus, we use
        :math:`\log (\\frac{c_Z}{n_Z})^{c_Z} + \log (\\frac{c_{Z^\mathrm{c}}}{n_{Z^\mathrm{c}}})^{c_{Z^\mathrm{c}}} - \log (\\frac{c_{[K]}}{n_{[K]}})^{c_{[K]}}`
        as the score.
    """
    def __init__(self, all_total_count, all_marked_count):
        self._all_total_count = all_total_count
        self._all_marked_count = all_marked_count

    def score(self, Z):
        nG = self._all_total_count
        cG = self._all_marked_count
        nZ = self.total_count(Z)
        cZ = self.marked_count(Z)
        ## Stopping criterion
        if nZ >= nG * .5:
            raise EchelonScanStop()
        nZc = nG - nZ
        cZc = cG - cZ
        ## Scores
        score = (cZ * (np.log(cZ) - np.log(nZ)) + cZc * (np.log(cZc) - np.log(nZc))) * ((cZ/nZ > cZc/nZc) * 1.)
        log_lambda = score - cG * np.log(cG / nG) * ((cZ/nZ > cZc/nZc) * 1.)
        return log_lambda, {'c(Z)': cZ,
                            #'raw_score': score, # score may be too small in typical use cases, and hence may be confusing.
                            'log_lambda': log_lambda}

    @abstractmethod
    def total_count(self, indices):
        pass

    @abstractmethod
    def marked_count(self, indices):
        pass


class PoissonScanOracleBase(ScanOracleBase):
    """
    Notes:
        Consider :math:`K` regions and let us denote :math:`[K] := \{1, 2, \ldots, K\}`.
        For each region :math:`k \in [K]`, assume :math:`c_k \sim \mathrm{Po}(\lambda_k)` and that :math:`\{c_k\}_{k \in [K]}` are independent.

        First, note that :math:`\mathrm{Po}(c; \lambda) := \\frac{\lambda^c e^{-\lambda}}{c!}` is maximized by :math:`\lambda = c`.
        Thus, the maximum likelihood given :math:`c` is :math:`\\frac{c^c e^{-c}}{c!}`.

        Consider a region :math:`Z \subset [K]`. We assign a score :math:`s` that indicates how "hot-spot-ish" the region :math:`Z` is.

        By the reproductive property, :math:`c_Z := \sum_{k \in Z} c_k \sim \mathrm{Po}(\lambda_Z)` where :math:`\lambda_Z = \sum_{k \in Z} \lambda_k`. Similarly for :math:`Z^\mathrm{c}`.

        We compare the maximum likelihood under :math:`\lambda_Z = \lambda_{Z^\mathrm{c}}` and :math:`\lambda_Z > \lambda_{Z^\mathrm{c}}`.
        The maximum log likelihood in the first case is :math:`\ell_0 := \log \\frac{c_{[K]}^{c_{[K]}} e^{-{c_{[K]}}}}{c_{[K]}!}`
        That for the second case is :math:`\ell_1 := \log \\frac{c_{Z}^{c_{Z}} e^{-{c_{Z}}}}{c_{Z}!} + \log \\frac{c_{Z^\mathrm{c}}^{c_{Z^\mathrm{c}}} e^{-{c_{Z^\mathrm{c}}}}}{c_{Z^\mathrm{c}}!}`

        Thus, we use
        :math:`(\ell_1 - \ell_0) [[c_Z > c_{Z^\mathrm{c}}]]`
        as the score.
    """
    def __init__(self, all_count, total_index_len):
        self.all_count = all_count
        self.total_index_len = total_index_len

    def _score(self, c):
        from math import lgamma
        return c * np.log(c) - c - lgamma(c)

    def score(self, Z):
        cG = self.all_count
        cZ = self.count(Z)
        ## Stopping criterion
        if len(Z) >= self.total_index_len * .5:
            raise EchelonScanStop()
        cZc = cG - cZ
        ## Scores
        log_lambda = (self._score(cZ) + self._score(cZc) - self._score(cG)) * (cZ/len(Z) > cZc/self.total_index_len)
        return log_lambda, {'c(Z)': cZ, 'log_lambda': log_lambda}

    @abstractmethod
    def count(self, indices):
        pass


class NdarrayBinomialScanOracle(ApproxBinomialScanOracleBase):
    """Hotspot scan oracle using approximate binomial score for numpy array data."""
    def __init__(self, total_count: np.ndarray, marked_count: np.ndarray):
        super().__init__(total_count.sum(), marked_count.sum())
        self.total_count_data = total_count.flatten()
        self.marked_count_data = marked_count.flatten()

    def total_count(self, indices: List[int]):
        return self.total_count_data[indices].sum()

    def marked_count(self, indices: List[int]):
        return self.marked_count_data[indices].sum()


class NdarrayPoissonScanOracle(PoissonScanOracleBase):
    """Hotspot scan oracle using Poisson score for numpy array data."""
    def __init__(self, data):
        super().__init__(data.sum(), len(data))
        self.data = data

    def count(self, indices):
        return self.data[indices].sum()


class DataFrameBinomialScanOracle(ApproxBinomialScanOracleBase):
    """Hotspot scan oracle using approximate binomial score for DataFrame data."""
    def __init__(self, df, id_colname: str, total_count_col: str, marked_count_col: str):
        super().__init__(df[total_count_col].sum(), df[marked_count_col].sum())
        self.df = df
        self.id_colname = id_colname
        self.total_count_col = total_count_col
        self.marked_count_col = marked_count_col

    def _subset(self, indices):
        return self.df[self.df[self.id_colname].isin(indices)]

    def total_count(self, indices):
        return self._subset(indices)[self.total_count_col].sum()

    def marked_count(self, indices):
        return self._subset(indices)[self.marked_count_col].sum()


class DataFramePoissonScanOracle(PoissonScanOracleBase):
    """Hotspot scan oracle using Poisson score for DataFrame data."""
    def __init__(self, df, id_colname: str, count_col: str):
        super().__init__(df[count_col].sum(), len(df))
        self.df = df
        self.id_colname = id_colname
        self.count_col = count_col

    def _subset(self, indices):
        return self.df[self.df[self.id_colname].isin(indices)]

    def count(self, indices):
        return self._subset(indices)[self.count_col].sum()
