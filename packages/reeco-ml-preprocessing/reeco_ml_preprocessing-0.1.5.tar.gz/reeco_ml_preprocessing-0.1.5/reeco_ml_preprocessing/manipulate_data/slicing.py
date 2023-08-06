from reeco_ml_preprocessing.base import BasePreprocessor


class DataSlicer(BasePreprocessor):

    def __init__(self, start_index: int = None, end_index: int = None):
        self.start_index = start_index
        self.end_index = end_index

    def transform(self, X):
        if self.start_index is None and self.end_index is None:
            return X
        elif self.start_index is None:
            return X[:self.end_index]
        elif self.end_index is None:
            return X[self.start_index:]
        else:
            return X[self.start_index:self.end_index]

    def fit_transform(self, X):
        return self.transform(X)