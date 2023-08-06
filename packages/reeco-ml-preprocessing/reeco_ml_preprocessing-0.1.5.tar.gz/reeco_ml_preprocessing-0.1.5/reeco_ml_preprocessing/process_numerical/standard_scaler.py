from typing import Union
import numpy as np
import pandas as pd
from reeco_ml_preprocessing.base import BasePreprocessor


class StandardScaler(BasePreprocessor):

    def __init__(self, target: str = None):
        self.target = target

    def fit(self, X: Union[pd.DataFrame, np.ndarray]):
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)

    def fit_transform(self, X: Union[pd.DataFrame, np.ndarray]):
        self.fit(X)
        return (X - self.mean) / self.std

    def transform(self, X: Union[pd.DataFrame, np.ndarray]):
        if isinstance(X, pd.DataFrame):
            for col in X.columns:
                pass
        if X.ndim == 1:
            return (X - self.mean[self.target]) / self.std[self.target]
        else:
            return (X - self.mean) / self.std

    def inverse_transform(self, X: Union[pd.DataFrame, np.ndarray]):
        if X.ndim == 1:
            return X * self.std[self.target] + self.mean[self.target]
        return X * self.std + self.mean