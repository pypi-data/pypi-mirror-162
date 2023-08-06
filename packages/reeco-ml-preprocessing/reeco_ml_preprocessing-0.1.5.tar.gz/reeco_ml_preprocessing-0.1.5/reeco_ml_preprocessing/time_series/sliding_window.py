from typing import Tuple, Union
import numpy as np
import pandas as pd

from reeco_ml_preprocessing.base import BasePreprocessor

class SlidingWindow(BasePreprocessor):
    """
    For every Series containing values `(t_0, t_1, t_2,..., t_l)`, transform
    into two 2D frame with `slides` columns. For example `(0, 1, 2, 3, 4)` when
    transforming with `slides = 2` will return:
    ```
    np.array([
        [0, 1],
        [1, 2],
        [2, 3]
    ])
    ```
    and
    np.array([[2], [3], [4]])
    The SlidingWindow will return 3D-numpy array, therefore a PandasNumpyTransformer
    will be attached within.

    Args:
    -------
    input_timesteps: int
        Input timesteps, i.e., number of columns in past dataframe
    output_timesteps: int. Depreciated
        Output timesteps, i.e., number of columns in future dataframe
        or the number of desired timesteps to be predicted.
    """

    def __init__(self, input_timesteps: int, output_timesteps: int, target: str):
        self.target = target
        self.input_timesteps = input_timesteps
        self.output_timesteps = output_timesteps

    def fit_transform(self, X: Union[pd.Series, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        if isinstance(X, pd.Series):
            rnp = self.get_historical_attributes(X).values
            return (rnp, rnp)

        elif isinstance(X, pd.DataFrame):
            n_examples = X.shape[0] - self.input_timesteps - self.output_timesteps + 1
            n_attr = len(X.columns)
            if n_examples < 1:
                rnp = np.zeros((1, n_attr, self.input_timesteps))
                for i, col in enumerate(X.columns):
                    rnp[:, i, :] = X[col].replace([np.inf, -np.inf], 0.0).fillna(0.0).T.values
                return rnp, None
            rnp = np.zeros((n_examples, n_attr, self.input_timesteps))
            tnp = np.zeros((n_examples, self.output_timesteps))
            for i, col in enumerate(X.columns):
                rnp[:, i, :] = self.get_historical_attributes(X[col])
            tnp[:] = self.get_historical_attributes(X[self.target], target=True)
            return (rnp, tnp)

    def transform(self, X: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        return self.fit_transform(X)

    def get_historical_attributes(self, series: pd.Series, target: bool = False) -> np.ndarray:
        series.fillna(0.0, inplace=True)
        df = pd.DataFrame()
        n_features = self.input_timesteps + self.output_timesteps
        
        for i in range(n_features):
            df[f'lag-{i}-{series.name}'] = series.shift(i)

        df.dropna(inplace=True)
        if not target:
            df = df.iloc[:, :self.input_timesteps].iloc[:, ::-1]
        else:
            df = df.iloc[:, -self.output_timesteps:]
        return df.values

