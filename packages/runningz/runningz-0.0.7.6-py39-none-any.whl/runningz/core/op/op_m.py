from statistics import median
import numpy as np
import pandas as pd
import polars as pl
import hashlib
from ._numba import OP_groupby_master


class OP_m:
    # ---------------------------------------- info ------------------------------------------
    # usable op
    op_list = [
        'sum', 'mean', 'std', 'min', 'max', 'median', 'var',
        'prod', 'sum_log', 'argmin', 'argmax', 
        'any', 'all',
    ]

    # example
    name_list = [
        'sum(n1, n2, n3)',
        'mean(n1, n2, n3)',
        'std(n1, n2, n3)',
        'min(n1, n2, n3)',
        'max(n1, n2, n3)',

        # 'median(n1, n2, n3)',
        'var(n1, n2, n3)',
        # 'prod(n1, n2, n3)',
        # 'sum_log(n1, n2, n3)',
        'argmin(n1, n2, n3)',
        'argmax(n1, n2, n3)',

        'any(n1, n2, n3)',
        'all(n1, n2, n3)',
    ]

    # ---------------------------------------- op(xs) ----------------------------------------
    def sum(xs):
        return np.nansum(xs, axis = 1).astype(np.float32)
    
    def mean(xs): 
        return np.nanmean(xs, axis = 1).astype(np.float32)

    def std(xs):
        return np.nanstd(xs, axis = 1).astype(np.float32)

    def min(xs):
        return np.nanmin(xs, axis = 1).astype(np.float32)

    def max(xs):
        return np.nanmax(xs, axis = 1).astype(np.float32)

    def median(xs):
        return np.median(xs, axis = 1).astype(np.float32)

    def var(xs):
        return np.nanvar(xs, axis = 1).astype(np.float32)   

    def prod(xs):
        return np.nanprod(xs, axis = 1).astype(np.float32)

    def sum_log(xs):
        return np.nansum(np.log(xs), axis = 1).astype(np.float32)

    def argmin(xs):
        return np.nanargmin(xs, axis = 1).astype(np.int32)

    def argmax(xs):
        return np.nanargmax(xs, axis = 1).astype(np.int32)
    
    def any(xs):
        return np.any(xs, axis = 1).astype(np.int32)
    
    def all(xs):
        return np.all(xs, axis = 1).astype(np.int32)

