from lunarcalendar import Converter, Solar
import numpy as np
import pandas as pd

class LunarConcater:

    def __init__(
        self,
        month: bool = True,
        day: bool = True,
        hour: bool = True,
        year: bool = False,
        minute: bool = False,
        second: bool = False
    ):
        self.mask = [year, month, day, hour, second, minute]
        # Note that all title must has prefix "static_" in order to differentiate between
        # static covariates and others
        self.title = [
            'static_lunar_year',
            'static_lunar_month',
            'static_lunar_day',
            'static_lunar_hour',
            'static_lunar_second',
            'static_lunar_minute'
        ]

    def transform(self, X: pd.DataFrame):
        n_components = len(self.mask)
        lunar_info = X.index.to_pydatetime()
        lunar_info = np.array([self.get_lunar_components(x) for x in lunar_info])
        lunar_col_kept = [self.title[i] for i in range(n_components) if self.mask[i]]
        
        df_lunar = pd.DataFrame(
            lunar_info[:, self.mask],
            columns=lunar_col_kept,
            index=X.index
        )
        return pd.concat([X, df_lunar], axis=1)
    
    def fit_transform(self, X: pd.DataFrame):
        return self.transform(X)

    def get_lunar_components(self, x: pd.DatetimeIndex):
        """Convert a Solar date into Lunar date"""
        lunar = Converter.Solar2Lunar(Solar(x.year, x.month, x.day))
        res = [lunar.year, lunar.month, lunar.day, x.hour, x.second, x.minute]
        return res
