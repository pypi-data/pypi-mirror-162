import numpy as np
import pandas as pd
import polars as pl
import hashlib


class OP_1:
    # ---------------------------------------- info ------------------------------------------
    # usable op
    op_list = [
        # op(x)
        'o', 'ffill', 
        'int32', 'int64', 'float32', 'float64', 'ceil', 'floor', 
        'neg', 'sign', 'abs',
        'inv', 'power', 'sqrt', 
        'log', 'log1p', 'log10', 'log_abs', 'exp', 'expm1',
        'rank', 'cumsum', '_not',

        # op(x, *agrs) 
        'fillna_v', 'linear_v', 'power_v', 'clip_v', 
        'rank_v', 'isin_v', 'bin_v',
        'eq_v', 'ge_v', 'le_v', 'gt_v', 'lt_v',

        'zscore_v',
    ]

    # example
    name_list = [
        'o(n1)',
        'ffill(n2)',
        'int32(n1)', 
        # 'int64(n1)',
        'float32(n1)', 
        # 'float64(n1)',
        'ceil(n1)', 
        'floor(n1)', 
        'neg(n1)',
        'sign(n1)',
        'abs(n1)',
        'inv(n1)',
        'power(n1)',
        'sqrt(n1)',
        'log(n1)',
        'log1p(n1)',
        'log10(n1)',
        'log_abs(n1)',
        'exp(n1)',
        'expm1(n1)',
        'rank(n1)',
        'cumsum(n1)',
        '_not(n1)',

        'fillna_v(n2, -1)',
        'linear_v(n1, 1, 0)',
        'power_v(n1, 2)',
        'clip_v(n1, 0, 2)',
        'rank_v(n1, dense, pct)',
        'isin_v(n1, 0,1)',
        'bin_v(n1, 10)',
        'eq_v(n1, 0)',
        'ge_v(n1, 0)',
        'le_v(n1, 0)',
        'gt_v(n1, 0)',
        'lt_v(n1, 0)',
    ]
    
    # ---------------------------------------- op(x) ----------------------------------------
    def o(x):
        return x

    def ffill(x):
        return pd.Series(x).fillna(method='ffill').values    

    def int32(x):
        return x.astype(np.int32)

    def int64(x):
        return x.astype(np.int64)

    def float32(x):
        return x.astype(np.float32)

    def float64(x):
        return x.astype(np.float64)

    def ceil(x):
        return np.ceil(x).astype(np.float32)
    
    def floor(x):
        return np.floor(x).astype(np.float32)
    
    def neg(x):
        return -1 * x

    def sign(x):
        return np.where(x >= 0, 1, -1).astype(np.float32)

    def abs(x):
        return np.abs(x)

    def inv(x):
        return (1 / x).astype(np.float32)

    def power(x):
        return x ** 2

    def sqrt(x):
        return (x ** 0.5).astype(np.float32)
    
    def log(x):
        return np.log(x).astype(np.float32)

    def log1p(x):
        return np.log1p(x).astype(np.float32)

    def log10(x):
        return np.log10(x).astype(np.float32)

    def log_abs(x):
        sign = np.where(x >= 0, 1.0, -1.0).astype(np.float32)
        return sign * np.log1p(np.abs(x)).astype(np.float32)

    def exp(x):
        return np.exp(x).astype(np.float32)

    def expm1(x):
        return np.expm1(x).astype(np.float32)            

    def rank(x):
        if type(x) == np.ndarray:
            return pd.Series(x).rank(method = 'dense', pct = True).values.astype(np.float32)
        ans = x.rank(method = 'dense')
        ans /= ans.max()
        return ans.cast(pl.datatypes.Float32)
   
    def cumsum(x):
        return np.cumsum(x).astype(np.float32)

    def _not(x):
        return (~x.astype(bool)).astype(np.int32)    

    # ---------------------------------------- op(x, *agrs) ----------------------------------------
    def fillna_v(x, v):
        return pd.Series(x).fillna(v).values

    def linear_v(x, a, b):
        return a * x + b

    def power_v(x, k):
        return x ** k

    def clip_v(x, _min, _max):
        return np.clip(x, _min, _max)

    def rank_v(x, method, pct):
        if type(x) == np.ndarray:
            return pd.Series(x).rank(method = method, pct = (pct == 'pct')).values.astype(np.float32)
        ans = x.rank(method = method)
        if pct == 'pct':
            ans /= ans.max()
        return ans.cast(pl.datatypes.Float32)

    def isin_v(x, *args):
        s = set(args)
        return pd.Series(x).isin(s).astype(np.int32).values

    def bin_v(x, k):
        x = x.copy()
        _min, _max = np.nanmin(x), np.nanmax(x)
        gap = (1e-6 + _max - _min) / k
        x[np.isnan(x)] = 0
        return np.int32((x - _min) // gap)
    
    # logi
    def eq_v(x, v):
        ans = np.zeros(len(x), dtype=np.float32)
        ans[x == v] = 1
        return ans

    def ge_v(x, v):
        ans = np.zeros(len(x), dtype=np.float32)
        ans[x >= v] = 1
        return ans  

    def le_v(x, v):
        ans = np.zeros(len(x), dtype=np.float32)
        ans[x <= v] = 1
        return ans     

    def gt_v(x, v):
        ans = np.zeros(len(x), dtype=np.float32)
        ans[x > v] = 1
        return ans  

    def lt_v(x, v):
        ans = np.zeros(len(x), dtype=np.float32)
        ans[x < v] = 1
        return ans               
    
    def zscore_v(x, a, b):
        return (x - a) / b