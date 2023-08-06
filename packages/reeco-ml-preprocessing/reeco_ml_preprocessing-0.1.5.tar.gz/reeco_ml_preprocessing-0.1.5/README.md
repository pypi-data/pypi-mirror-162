# Reeco ML Preprocessing Library

Module for preprocessor

## Prerequisite

It is recommended to use Python 3.9 64bit since it is the environment that we developed the package.

## Installation

Using `pip`:

```
$ pip install reeco_ml_preprocessing
```

or

```
$ py -m pip reeco_ml_preprocessing
```

### Example

```python
import numpy as np
from reeco_ml_preprocessing import PreprocessPipeline
from reeco_ml_preprocessing.time_series.ts_imputer import TimeSeriesImputer

pipeline = PreprocessPipeline(
    [TimeSeriesImputer(method='linear')]
)
X = pd.DataFrame(
    {
        "a": 1, 2, 3, np.nan, 5
        "b": 0, 1, np.nan, np.nan, 4
    }
)
pipeline.fit_transform(X)
```