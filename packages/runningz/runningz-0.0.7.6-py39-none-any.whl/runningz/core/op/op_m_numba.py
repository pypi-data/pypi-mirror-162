import numpy as np
import pandas as pd
import polars as pl
import numba
from numba import njit
from ._numba import get_idx_all

class OP_m_numba:
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

        'median(n1, n2, n3)',
        'var(n1, n2, n3)',
        'prod(n1, n2, n3)',
        'sum_log(n1, n2, n3)',
        'argmin(n1, n2, n3)',
        'argmax(n1, n2, n3)',

        'any(n1, n2, n3)',
        'all(n1, n2, n3)',
    ]

    # ---------------------------------------- op(xs) ----------------------------------------
    @njit(nopython=True)
    def _numba_sum(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nansum(xs[i, :])
        return ans
    
    @njit(nopython=True)
    def _numba_mean(xs): 
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nanmean(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_std(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nanstd(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_min(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nanmin(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_max(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nanmax(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_median(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.median(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_var(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nanvar(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_prod(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nanprod(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_sum_log(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.nansum(np.log(xs[i, :]))
        return ans

    @njit(nopython=True)
    def _numba_argmin(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.argmin(xs[i, :])
        return ans

    @njit(nopython=True)
    def _numba_argmax(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.argmax(xs[i, :])
        return ans
    
    @njit(nopython=True)
    def _numba_any(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.any(xs[i, :])
        return ans
    
    @njit(nopython=True)
    def _numba_all(xs):
        n = len(xs)
        ans = np.zeros(n, dtype=np.float32)
        for i in range(n):
            ans[i] = np.all(xs[i, :])
        return ans

    # ---------------------------------------- adapter ----------------------------------------
    _numba_func_dict = {
        'sum': _numba_sum,
        'mean': _numba_mean,
        'std': _numba_std,
        'min': _numba_min,
        'max': _numba_max,
        'median': _numba_median,
        'var': _numba_var,
        'prod': _numba_prod,
        'sum_log': _numba_sum_log,
        'argmin': _numba_argmin,
        'argmax': _numba_argmax,
        'any': _numba_any,
        'all': _numba_all,
    }

    @njit(nopython=True, parallel=True)
    def _numba_multi(func, x, idx_all, idx_all_p1p2):
        ans = np.zeros(len(x), dtype = np.float32)
        n = len(idx_all_p1p2) - 1
        for i in numba.prange(0, n):
            idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
            ans[idx] = func(x[idx])
        return ans

    def numba_m(op, x, df_name, idx_all_DICT, idx_all_p1p2_DICT):
        df_name = f'{df_name}_global'
        if df_name not in idx_all_p1p2_DICT:
            n = len(x)
            idx = list(range(0, n, max(1, n // 1024)))
            idx += [] if idx[-1] == n else [n]
            idx_list = [np.arange(idx[i], idx[i + 1], dtype = np.uint32) for i in range(len(idx) - 1)]
            idx_all, idx_all_p1p2 = get_idx_all(idx_list)
            idx_all_DICT[df_name] = idx_all
            idx_all_p1p2_DICT[df_name] = idx_all_p1p2
        else:
            idx_all = idx_all_DICT[df_name]
            idx_all_p1p2 = idx_all_p1p2_DICT[df_name]
        
        # ans = eval(f'OP_m_numba._numba_multi(OP_m_numba.{op}, x, idx_all, idx_all_p1p2)')
        ans = OP_m_numba._numba_multi(OP_m_numba._numba_func_dict[op], x, idx_all, idx_all_p1p2)
        return ans

