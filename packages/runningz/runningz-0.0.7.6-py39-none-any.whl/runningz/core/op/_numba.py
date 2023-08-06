import numpy as np
import pandas as pd
import polars as pl
import warnings, time
warnings.filterwarnings('ignore')
import numba
from numba import njit
from ._numba_2 import _numba_2_diff_sum, _numba_2_diff_abs_sum, _numba_2_diff_mean, _numba_2_diff_abs_mean
from ._numba_2 import _numba_2_corr, _numba_2_beta, _numba_2_alpha

@njit(nopython = True)
def _numba_sum(a, k, is_time = 0):
    # dict
    _n = 0
    n = len(a)
    ans_i = 0
    cnt_nan = 0
    
    # rolling
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(_n, _n + n):
        # add
        v2 = a[p2, 0]
        if np.isnan(v2):
            cnt_nan += 1
        else:
            ans_i += v2  
        
        while True:
            if is_time == 1:
                if a[p2, -1] - a[p1, -1] + 1 <= k: break   
            else:
                if p2 - p1  + 1 <= k: break
            
            # remove
            v1 = a[p1, 0]
            p1 += 1
            if np.isnan(v1):
                cnt_nan -= 1
            else:
                ans_i -= v1
        
        # get value
        if p2 - p1 + 1 - cnt_nan == 0:
            ans[p2 - _n] = np.nan
        else: 
            ans[p2 - _n] = ans_i
    
    # return history _data
    a = a[p1: p2 + 1]
    return ans

@njit(nopython = True)
def _numba_mean(a, k, is_time = 0):
    # dict
    _n = 0
    n = len(a)
    ans_i = 0
    s = 0
    cnt_nan = 0
    
    # rolling
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(_n, _n + n):
        # add
        v2 = a[p2, 0]
        if np.isnan(v2):
            cnt_nan += 1
        else:
            s += v2  
        
        while True:
            if is_time == 1:
                if a[p2, -1] - a[p1, -1] + 1 <= k: break   
            else:
                if p2 - p1  + 1 <= k: break
              
            # remove
            v1 = a[p1, 0]
            p1 += 1
            if np.isnan(v1):
                cnt_nan -= 1
            else:
                s -= v1
        
        # get value
        if p2 - p1 + 1 - cnt_nan == 0:
            ans[p2 - _n] = np.nan
        else:
            ans_i = s / (p2 - p1 + 1 - cnt_nan)    
            ans[p2 - _n] = ans_i
    
    # return history _data
    a = a[p1: p2 + 1]
    return ans

@njit(nopython = True)
def _numba_min(a, k, is_time = 0):
    # dict
    _n = 0
    n = len(a)
    ans_i = a[0,0]
    cnt_nan = 0
    
    # rolling
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(_n, _n + n):
        # add
        v2 = a[p2, 0]
        if np.isnan(v2):
            cnt_nan += 1
        else:
            if v2 < ans_i:
                ans_i = v2
        
        while True:
            if is_time == 1:
                if a[p2, -1] - a[p1, -1] + 1 <= k: break   
            else:
                if p2 - p1  + 1 <= k: break
            
            # remove
            v1 = a[p1, 0]
            p1 += 1
            if np.isnan(v1):
                cnt_nan -= 1
            else:
                if v1 == ans_i:
                    ans_i = np.nanmin(a[p1: p2 + 1, 0])
                
        # get value
        if p2 - p1 + 1 - cnt_nan == 0:
            ans[p2 - _n] = np.nan
        else:
            # ans_i = np.nanmin(a[p1: p2 + 1, 0])
            ans[p2 - _n] = ans_i

    # return history _data
    a = a[p1: p2 + 1]
    return ans


@njit(nopython = True)
def _numba_max(a, k, is_time = 0):
    # dict
    _n = 0
    n = len(a)
    ans_i = a[0,0]
    cnt_nan = 0
    
    # rolling
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(_n, _n + n):
        # add
        v2 = a[p2, 0]
        if np.isnan(v2):
            cnt_nan += 1
        else:
            if v2 > ans_i:
                ans_i = v2
        
        while True:
            if is_time == 1:
                if a[p2, -1] - a[p1, -1] + 1 <= k: break   
            else:
                if p2 - p1  + 1 <= k: break
            
            # remove
            v1 = a[p1, 0]
            p1 += 1
            if np.isnan(v1):
                cnt_nan -= 1
            else:
                if v1 == ans_i:
                    ans_i = np.nanmax(a[p1: p2 + 1, 0])
                
        # get value
        if p2 - p1 + 1 - cnt_nan == 0:
            ans[p2 - _n] = np.nan
        else:
            # ans_i = np.nanmin(a[p1: p2 + 1, 0])
            ans[p2 - _n] = ans_i

    # return history _data
    a = a[p1: p2 + 1]
    return ans


@njit(nopython = True)
def _numba_std(a, k, is_time = 0):
    # dict
    _n = 0
    n = len(a)
    ans_i = 0
    cnt_nan = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(_n, _n + n):
        # add
        v2 = a[p2, 0]
        if np.isnan(v2):
            cnt_nan += 1
        
        while True:
            if is_time == 1:
                if a[p2, -1] - a[p1, -1] + 1 <= k: break   
            else:
                if p2 - p1  + 1 <= k: break
            
            # remove
            v1 = a[p1, 0]
            p1 += 1
            if np.isnan(v1):
                cnt_nan -= 1
       
        # get value
        if p2 - p1 + 1 - cnt_nan == 0:
            ans[p2 - _n] = np.nan       
        else:
            ans_i = np.nanstd(a[p1: p2 + 1, 0])    
            # ans_i = _get_median(a[p1: p2 + 1, 0])
            ans[p2 - _n] = ans_i

    # return history _data
    a = a[p1: p2 + 1]
    return ans

@njit(nopython = True)
def _numba_median(a, k, is_time = 0):
    # dict
    _n = 0
    n = len(a)
    ans_i = 0
    cnt_nan = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(_n, _n + n):
        # add
        v2 = a[p2, 0]
        if np.isnan(v2):
            cnt_nan += 1
        
        while True:
            if is_time == 1:
                if a[p2, -1] - a[p1, -1] + 1 <= k: break   
            else:
                if p2 - p1  + 1 <= k: break
            
            # remove
            v1 = a[p1, 0]
            p1 += 1
            if np.isnan(v1):
                cnt_nan -= 1
       
        # get value
        if p2 - p1 + 1 - cnt_nan == 0:
            ans[p2 - _n] = np.nan       
        else:
            ans_i = np.nanmedian(a[p1: p2 + 1, 0])    
            # ans_i = _get_median(a[p1: p2 + 1, 0])
            ans[p2 - _n] = ans_i

    # return history _data
    a = a[p1: p2 + 1]
    return ans

@njit(nopython = True)
def _numba_ewm(a, k, is_time = 0):
    n = len(a)
    ans = np.zeros(n, dtype = np.float64)
    ans[0] = a[0, 0]
    for i in range(1, n):
        ans[i] = ans[i - 1] * (1 - k) + a[i, 0] * k
    return ans

@njit(nopython=True)
def _numba_shift(a, k = 0, is_time = 0):
    if k == 0:
        ans = a[:, 0].astype(np.float64)
    elif k > 0:
        ans = np.vstack((a[-k:] * np.nan, a[:-k]))[:, 0]
    else:
        ans = np.vstack((a[-k:], a[k:] * np.nan))[:, 0]
    return ans


# ---------------------------------------- _numba_agg ----------------------------------------
@njit(nopython=True, fastmath=True)
def _numba_agg_sum(x):
    return np.nansum(x)

@njit(nopython=True, fastmath=True)
def _numba_agg_mean(x):
    return np.nanmean(x)

@njit(nopython=True, fastmath=True)
def _numba_agg_min(x):
    return np.nanmin(x)

@njit(nopython=True, fastmath=True)
def _numba_agg_max(x):
    return np.nanmax(x)

@njit(nopython=True, fastmath=True)
def _numba_agg_std(x):
    return np.nanstd(x)

@njit(nopython = True)
def _numba_agg_rank(a): # need sort
    n = len(a)
    ans = np.zeros(n, dtype = np.float64)
    ai = 0
    
    i = 0
    while i < n:
        j = i + 1
        while j < n and a[j, 0] == a[i, 0]:
            j += 1
        v = (i + j + 1) / 2
        
        while ai < j:
            ans[ai] = v
            ai += 1
        i = j
    ans /= n
    return ans

# ---------------------------------------- call numba ----------------------------------------
_numba_func_dict = {
    # roll
    'roll_mean': _numba_mean,
    'roll_std': _numba_std,
    'roll_min': _numba_min,
    'roll_max': _numba_max,
    'roll_sum': _numba_sum,
    'roll_median': _numba_median,
    'roll_ewm': _numba_ewm,
    'roll_shift': _numba_shift,
    
    # roll_numba_2
    'roll_diff_sum': _numba_2_diff_sum,
    'roll_diff_abs_sum': _numba_2_diff_abs_sum,
    'roll_diff_mean': _numba_2_diff_mean,
    'roll_diff_abs_mean': _numba_2_diff_abs_mean,
    'roll_corr': _numba_2_corr,
    'roll_beta': _numba_2_beta,
    'roll_alpha': _numba_2_alpha,

    # agg
    'agg_sum': _numba_agg_sum,
    'agg_mean': _numba_agg_mean,
    'agg_min': _numba_agg_min,
    'agg_max': _numba_agg_max,
    'agg_std': _numba_agg_std,
    'agg_rank': _numba_agg_rank,
    
    # groupby
    'gp_sum': _numba_agg_sum,
    'gp_mean': _numba_agg_mean,
    'gp_min': _numba_agg_min,
    'gp_max': _numba_agg_max,
    'gp_std': _numba_agg_std,
}

_numba_roll_mean =  _numba_mean,
_numba_roll_std = _numba_std,
_numba_roll_min = _numba_min,
_numba_roll_max = _numba_max,
_numba_roll_sum = _numba_sum,
_numba_roll_median = _numba_median,
_numba_roll_ewm = _numba_ewm,
_numba_roll_shift = _numba_shift,

_numba_gp_sum = _numba_agg_sum
_numba_gp_mean = _numba_agg_mean
_numba_gp_min = _numba_agg_min
_numba_gp_max = _numba_agg_max
_numba_gp_std = _numba_agg_std


@njit(nopython=True, parallel=True)
def _numba_roll(op_func, a, idx_all, idx_all_p1p2, k):
    ans = np.zeros(len(a), dtype=np.float32)
    n = len(idx_all_p1p2) - 1
    for i in numba.prange(0, n):
        idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
        ans[idx] = op_func(a[idx] , k)  
    return ans

@njit(nopython=True, parallel=True)
def _numba_roll_sort(op_func, a, idx_all, idx_all_p1p2, k):
    ans = np.zeros(len(a), dtype=np.float32)
    n = len(idx_all_p1p2) - 1
    for i in numba.prange(0, n):
        idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
        idx_sorted = idx[np.argsort(a[idx, -1])] 
        s = op_func(a[idx_sorted] , k)  
        ans[idx_sorted] = s
    return ans    

@njit(nopython=True, parallel=True)
def _numba_agg(op_func, a, idx_all, idx_all_p1p2):
    ans = np.zeros(len(a), dtype=np.float32)
    n = len(idx_all_p1p2) - 1
    for i in numba.prange(0, n):
        idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
        ans[idx] = op_func(a[idx])  
    return ans

@njit(nopython=True, parallel=True)
def _numba_agg_sort(op_func, a, idx_all, idx_all_p1p2):
    ans = np.zeros(len(a), dtype=np.float32)
    n = len(idx_all_p1p2) - 1
    for i in numba.prange(0, n):
        idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
        idx_sorted = idx[np.argsort(a[idx, -1])] 
        ans[idx_sorted] = op_func(a[idx_sorted])  
    return ans    

@njit(nopython=True, parallel=True)
def _numba_gp(op_func, a, idx_all, idx_all_p1p2):
    ans = np.zeros(len(idx_all_p1p2) - 1, dtype=np.float32)
    n = len(idx_all_p1p2) - 1
    for i in numba.prange(0, n):
        idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
        ans[i] = op_func(a[idx])  
    return ans


# ---------------------------------------- call no numba ----------------------------------------
def _agg_count(a):
    return len(a)
def _agg_nan(a):
    return np.isnan(a).sum()
def _agg_nonan(a):
    return (~np.isnan(a)).sum()
_func_dict = {
    'agg_count': _agg_count,
    'agg_nan': _agg_nan,
    'agg_nonan': _agg_nonan,
}
def _agg(op_func, a, idx_all, idx_all_p1p2):
    ans = np.zeros(len(a), dtype=np.float32)
    n = len(idx_all_p1p2) - 1
    for i in numba.prange(0, n):
        idx = idx_all[idx_all_p1p2[i]: idx_all_p1p2[i + 1]]
        ans[idx] = op_func(a[idx])  
    return ans    

# ---------------------------------------- main ----------------------------------------
def get_idx_all(idx_list):
    n = len(idx_list)
    idx_all_p1p2 = np.zeros(n + 1).astype(np.uint32)
    for i in range(n):
        idx_all_p1p2[i + 1] = idx_all_p1p2[i] + len(idx_list[i])
    idx_all = np.hstack(idx_list).astype(np.uint32)
    return idx_all, idx_all_p1p2


def OP_groupby_master(df, keys, cols, op, col_time, k, 
                    idx_all_DICT, idx_all_p1p2_DICT, df_name_keys, a_keys_DICT, mask):
    if type(df) == pd.DataFrame:
        df = pl.DataFrame(df)
        
    if df_name_keys not in idx_all_p1p2_DICT:
        # print(f' ------------------------- {df_name_keys} ------------------------- ')
        df_gp = df.groupby(keys).groups().to_numpy()
        a_keys = df_gp[:,:len(keys)]
        a_keys_DICT[df_name_keys] = a_keys
        idx_list = df_gp[:,len(keys)]
        idx_all, idx_all_p1p2 = get_idx_all(idx_list)
        idx_all_DICT[df_name_keys] = idx_all
        idx_all_p1p2_DICT[df_name_keys] = idx_all_p1p2
    else:
        idx_all = idx_all_DICT[df_name_keys]
        idx_all_p1p2 = idx_all_p1p2_DICT[df_name_keys]
    
    # get a
    col = cols[0]
    if op in ['agg_count', 'agg_nonan',  'agg_nan']:
        a = df[col].to_numpy().reshape(-1, 1).astype(np.float32)  
        sort = False
    elif op in ['agg_rank']:
        a = df[col].to_numpy().reshape(-1, 1).astype(np.float32)  
        sort = True
    else:
        if len(cols) == 1:
            a = df[col].to_numpy().reshape(-1, 1).astype(np.float32)   
        else:
            a = df[cols].to_numpy().astype(np.float32)   
        sort = False
    
    # mask
    if mask is not None:
        a = np.where(mask.reshape(-1, 1) == 1, a, np.nan) # mask == 0, set nan
    

    # go
    if op.startswith('roll_'):
        if sort:
            s = _numba_roll_sort(_numba_func_dict[op], a, idx_all, idx_all_p1p2, k)
        else:
            s = _numba_roll(_numba_func_dict[op], a, idx_all, idx_all_p1p2, k)
        # s = eval(f'_numba_roll(_numba_{op}, a, idx_all, idx_all_p1p2, k)')
    
    elif op.startswith('agg_'):
        if op in ['agg_count', 'agg_nan', 'agg_nonan']:
            s = eval(f'_agg(_{op}, a, idx_all, idx_all_p1p2)')
        else:
            if sort:
                s = eval(f'_numba_agg_sort(_numba_{op}, a, idx_all, idx_all_p1p2)')
            else:
                # s = _numba_agg(_numba_func_dict[op], a, idx_all, idx_all_p1p2, k)
                s = eval(f'_numba_agg(_numba_{op}, a, idx_all, idx_all_p1p2)')
    
    elif op.startswith('gp_'):
        # s = _numba_gp(_numba_func_dict[op], a, idx_all, idx_all_p1p2, k)
        s = eval(f'_numba_gp(_numba_{op}, a, idx_all, idx_all_p1p2)')
    return s#.astype(np.float32)
