from typing import List

import joblib


class PreprocessPipeline:

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def save(self, path):
        """Save the processor to expected `path` as a `.joblib` file."""
        joblib.dump(self, path)

    def fit(self):
        pass

    def transform(self, X):
        for p in self.pipeline:
            if hasattr(p, "transform"):
                X = p.transform(X)
        return X

    def fit_transform(self, X):
        for p in self.pipeline:
            if hasattr(p, "fit_transform"):
                X = p.fit_transform(X)
        return X

    def inverse_transform(self, X):
        for p in reversed(self.pipeline):
            if hasattr(p, "inverse_transform"):
                X = p.inverse_transform(X)
        return X