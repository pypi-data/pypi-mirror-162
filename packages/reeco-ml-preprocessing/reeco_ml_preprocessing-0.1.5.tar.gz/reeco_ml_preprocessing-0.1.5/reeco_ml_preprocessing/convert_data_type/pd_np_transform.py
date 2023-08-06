import numpy as np
import pandas as pd
from reeco_ml_preprocessing.base import BasePreprocessor

class PandasNumpyTransformer(BasePreprocessor):
    """
    Transform a Dataframe into Numpy ndarray while keeping the column and
    indices for inverse transformation.
    """

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        self.columns_ = X.columns
        self.indices_ = X.index
        return X.values

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        self.indices_ = X.index
        return X.values

    def inverse_transform(self, X) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame) and not isinstance(X, pd.Series):
            return pd.DataFrame(X, columns=self.columns_)
        else:
            return X
