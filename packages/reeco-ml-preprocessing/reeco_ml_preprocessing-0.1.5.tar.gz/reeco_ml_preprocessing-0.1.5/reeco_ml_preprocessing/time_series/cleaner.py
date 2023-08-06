from typing import Union

import pandas as pd


class TimeSeriesCleaner():
    """
    The TimeSeriesCleaner perform must-preprocessed steps for timeseries data.
    These includes:
    
    1. Set datetime column as index.
    2. Remove null rows exists in the label column.
    3. Align datetime index.
    """

    def __init__(
        self,
        date_col: Union[str, pd.Index],
        label_col: Union[str, pd.Index],
        sampling_rule: str,
        time_lag: str,
        limit: int = None
    ):
        self.date_col       = date_col
        self.label_col      = label_col
        self.sampling_rule  = sampling_rule
        self.time_lag       = time_lag
        self.limit          = limit

    def remove_null_rows(self, X):
        X = X.dropna(how='all')
        return X

    def set_index(self, X, date_col) -> pd.DataFrame:
        """Resample and set index. All categorical variable will also be removed."""
        if date_col not in X.columns:
            raise KeyError("{} does not appear in your data columns".format(date_col))

        try:
            # Check if the column can be converted to datetime
            X[date_col] = pd.to_datetime(X[date_col])
        except:
            raise ValueError("The expected date time column does not have the correct format. \
                Try to choose different column or change its format.")
        X = X.set_index(date_col).sort_index()
        return X

    def align_time(self, X, sampling_rule: str, time_lag: str, limit: int = None):
        """Align time to sampling_rule."""
        base = '1H' if sampling_rule.endswith('H') else sampling_rule
        index = pd.date_range(
            start=X.index[0],
            end=X.index[-1],
            freq=sampling_rule
        )
        # Fillna to 0 if all NaN within a column
        X = X.apply(lambda x: x.reindex(
            index,
            method='nearest',
            tolerance=time_lag
        ))
        if limit is not None:
            X = X[-limit:]
        return X

    def fit(self, X):
        X = self.set_index(X, self.date_col)
        X = self.remove_null_rows(X)
        X = self.align_time(X, self.sampling_rule, self.time_lag, self.limit)
        return X

    def fit_transform(self, X):
        return self.fit(X)

    def transform(self, X):
        return self.fit(X)
