class BasePreprocessor:

    def __init__(self):
        pass

    def fit(self, X):
        pass

    def transform(self, X):
        raise NotImplementedError

    def fit_transform(self, X):
        self.fit(X).transform(X)

    def inverse_transfrom(self, X):
        pass