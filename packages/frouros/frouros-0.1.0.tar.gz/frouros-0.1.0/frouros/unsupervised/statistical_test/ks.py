"""KSTest (Kolmogorov-Smirnov test) module."""

import numpy as np  # type: ignore
from scipy.stats import ks_2samp  # type: ignore

from frouros.unsupervised.base import NumericalData, UnivariateType
from frouros.unsupervised.statistical_test.base import (
    StatisticalTestBaseEstimator,
    TestResult,
)


class KSTest(StatisticalTestBaseEstimator):
    """KSTest (Kolmogorov-Smirnov test) algorithm class."""

    def __init__(self) -> None:
        """Init method."""
        super().__init__(data_type=NumericalData(), statistical_type=UnivariateType())

    def _statistical_test(
        self, X_ref_: np.ndarray, X: np.ndarray, **kwargs  # noqa: N803
    ) -> TestResult:
        test = ks_2samp(
            data1=X_ref_,
            data2=X,
            alternative=kwargs.get("alternative", "two-sided"),
            mode=kwargs.get("method", "auto"),
        )
        test = TestResult(statistic=test.statistic, p_value=test.pvalue)
        return test
