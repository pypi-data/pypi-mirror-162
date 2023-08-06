import pandas as pd
from reeco_ml_preprocessing.base import BasePreprocessor

from reeco_ml_preprocessing.time_series.simple_imputer import _mean_fill, _median_fill, _backward_fill, _forward_fill


class TimeSeriesImputer(BasePreprocessor):

    def __init__(self, method):
        """
        Method initialization for imputer.

        Args:
        -------
        method: String, default='linear'
            Custom kind to fill missing value.
            'linear': Use linear interpolation within each column.
            'backward': Use backward fill. Apply forward fill with remaining missing values in last columns.
            'forward': Use forward fill. Apply backward fill with remaining missing values in first columns.
            'mean': Replace by mean.
            'median': Replace by median.
        """
        self.method = method
        self.columns_ = None
        self.indices_ = None

    def fit(self):
        if self.method not in ["forward", "backward", "median", "mean", "linear"]:
            raise ValueError("Method {} is not exists".format(self.method))
        return self

    def fit_transform(self, X: pd.DataFrame):
        """
        Fill missing value with custom technique.

        Args:
        -------
        X: DataFrame
            Samples.
        save_columns_and_indices: Boolean
            When using fit, save the columns and indices for inverse transform later.
        create_date_col: Boolean
            When using fit, add an Time column with type float, which is retrieved from
            the indices.

        Returns:
        -------
        X_new: DataFrame
            Samples with filled values.
        """
        self.fit()
        X_new = self._impute(X, self.method)
        self.columns_ = X.columns
        self.indices_ = X.index
        return X_new

    def transform(self, X: pd.DataFrame):
        self.indices_ = X.index
        X_new = self._impute(X, self.method)
        return X_new

    def _impute(self, X: pd.DataFrame, method: str):
        if method == "forward":
            X = _forward_fill(X)
        elif method == "backward":
            X = _backward_fill(X)
        elif method == "median":
            X = _median_fill(X)
        elif method == "mean":
            X = _mean_fill(X)
        elif method == "linear":
            X = self._linear_fill(X)
        else:
            raise Exception("Cannot found method {}".format(method))
        return X.fillna(0.0)

    def _linear_fill(self, X):
        return _backward_fill(X.interpolate(method='linear'))
