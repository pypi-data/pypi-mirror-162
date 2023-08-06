import pandas as pd


def _backward_fill(X):
    return X.fillna(method="bfill").fillna(method="ffill")

def _forward_fill(X):
    return X.fillna(method="ffill").fillna(method="bfill")

def _mean_fill(X):
    if isinstance(X, pd.DataFrame):
        for i in X.columns[X.isnull().any(axis=0)]:
            X[i].fillna(X[i].mean(), inplace=True)
    else:
        X.fillna(X.mean(), inplace=True)
    return X

def _median_fill(X):
    if isinstance(X, pd.DataFrame):
        for i in X.columns[X.isnull().any(axis=0)]:
            X[i].fillna(X[i].median(), inplace=True)
    else:
        X.fillna(X.median(), inplace=True)
    return X