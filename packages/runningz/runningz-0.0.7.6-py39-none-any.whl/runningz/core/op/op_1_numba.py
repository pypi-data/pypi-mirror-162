import numpy as np
import pandas as pd
import polars as pl
import numba
from numba import njit
from ._numba import get_idx_all

class OP_1_numba:
    # ---------------------------------------- info ------------------------------------------
    # usable op
    op_list = [
        'numba_log_abs',
    ]
    # example
    name_list = [
        'numba_log_abs(n1)'
    ]

    # ---------------------------------------- op(x) ----------------------------------------
    @njit(nopython=True)
    def numba_log_abs(x): # 1e6row, 1e3col, 18s -> 5s
        sign = np.where(x >= 0, 1.0, -1.0)
        return (sign * np.log1p(np.abs(x)))


    # ---------------------------------------- adapter ----------------------------------------
    @njit(nopython=True, parallel=True)
    def _numba_single(func, x, idx_all, idx_all_p1p2):
        ans = np.zeros(len(x), dtype = np.float32)
        n = len(idx_all_p1p2) - 1
        for i in numba.prange(0, n):
            idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
            ans[idx] = func(x[idx])
        return ans

    def numba_1(op, x, df_name, idx_all_DICT, idx_all_p1p2_DICT, *args):
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
        
        ans = eval(f'OP_1_numba._numba_single(OP_1_numba.{op}, x, idx_all, idx_all_p1p2)')
        return ans

