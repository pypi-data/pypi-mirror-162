import numpy as np
import pandas as pd
import polars as pl
import warnings, time
warnings.filterwarnings('ignore')
import numba
from numba import njit


@njit(nopython = True)
def _numba_sum(t_L, t_R, v_R, shift_t, shift_k, win_k, is_time):
    is_cur = 0
    # t_L: 主表的时间列
    # t_R: 副表的时间列
    # v_R: 副表的待统计列
    # shift_t: 副表数据滞后主表shift_t秒, t_R[p2 + shift_k] <= t_L[pLeft] - shift_t
    # shift_k: 副表数据滞后主表shift_k条, t_R[p2 + shift_k] <= t_L[pLeft] - shift_t
    # win_k: 窗口的大小, win_k条, 或者win_k秒
    # is_time: 是否时间窗口. is_time=1时窗口为win_k秒, 其他为win_k条
    # is_cur: 为单表, 同一时间多条样本时, 确定当前样本. 统一拼表和单表的rolling函数

#     debug = True
#     def _print(title, ans_i, cnt_nan, pL, p1, p2, p2_next):
#         print('[{}] ans_i = {}, cnt_nan = {}, pL = {}, p1 = {}, p2 = {}, p2_next = {}'.\
#             format(title.ljust(9), ans_i, cnt_nan, pL, p1, p2, p2_next))
    
    # ==================================================
    # basic    
    n_L, n_R = len(t_L), len(t_R)
    ans = np.zeros(n_L, dtype = np.float64)
        
    ans_i, cnt_nan, p1, p2 = 0, 0, 0, -1 # init status
    for pL in range(n_L):
        # ==================================================
        # get_p2
        p2_next = p2 + shift_k + 1
        while p2_next < 0 or (p2_next < n_R and t_L[pL] - shift_t >= t_R[p2_next]):
            # for df_L == df_R, shift_k from current position, @zhongrunxing
            if is_cur ==  1 and p2_next > pL: break
            
            # if debug: _print('get_p2', ans_i, cnt_nan, pL, p1, p2, p2_next)
            # move p2
            p2 += 1 
            p2_next = p2 + shift_k + 1
            
            # add v_R[p2]
            v2 = v_R[p2] if p2 < n_R else np.nan
            if np.isnan(v2):
                cnt_nan += 1
            else:
                ans_i += v2  
        
        # ==================================================
        #  get_p1
        while p1 < n_R and p1 <= p2:
            # if debug: _print('get_p1', ans_i, cnt_nan, pL, p1, p2, p2_next)
            if is_time == 1:
                if t_L[pL] - shift_t - t_R[p1] + 1 <= win_k: break   
            else:
                if p2 - p1  + 1 <= win_k: break
            
            # remove v_R[p1]
            v1 = v_R[p1] if p1 < n_R else np.nan
            if np.isnan(v1):
                cnt_nan -= 1
            else:
                ans_i -= v1
            
            # move p1
            p1 += 1
        
        # ==================================================
        # get_value
        # if debug: _print('get_value', ans_i, cnt_nan, pL, p1, p2, p2_next)
        if p2 - p1  + 1 - cnt_nan <= 0:
            ans[pL] = np.nan
        else: 
            p2_end = p2 + 1 if p2 + 1 <= n_R else n_R
            # ans[pL] = np.nansum(v_R[p1: p2_end])
            ans[pL] = ans_i
            
    return ans


# @njit(nopython = True)
# def _numba_sum(t_L, t_R, v_R, shift_t, shift_k, win_k, is_time):
#     is_cur = 0
#     n_L, n_R = len(t_L), len(t_R)
#     ans = np.zeros(n_L, dtype = np.float64)
        
#     ans_i, cnt_nan, p1, p2 = 0, 0, 0, -1 # init status
#     for pL in range(n_L):
#         # ==================================================
#         # get_p2
#         p2_next = p2 + shift_k + 1
#         while p2_next < 0 or (p2_next < n_R and t_L[pL] - shift_t >= t_R[p2_next]):
#             if is_cur ==  1 and p2_next > pL: break
            
#             # move p2
#             p2 += 1 
#             p2_next = p2 + shift_k + 1
            
#             # add v_R[p2]
#             v2 = v_R[p2] if p2 < n_R else np.nan
#             if np.isnan(v2):
#                 cnt_nan += 1
          
#         # ==================================================
#         #  get_p1
#         while p1 < n_R and p1 <= p2:
#             if is_time == 1:
#                 if t_L[pL] - shift_t - t_R[p1] + 1 <= win_k: break   
#             else:
#                 if p2 - p1  + 1 <= win_k: break
            
#             # remove v_R[p1]
#             v1 = v_R[p1] if p1 < n_R else np.nan
#             if np.isnan(v1):
#                 cnt_nan -= 1
            
#             # move p1
#             p1 += 1
        
#         # ==================================================
#         # get_value
#         if p2 - p1  + 1 - cnt_nan <= 0:
#             ans[pL] = np.nan
#         else: 
#             p2_end = p2 + 1 if p2 + 1 <= n_R else n_R
#             ans[pL] = np.nansum(v_R[p1: p2_end])  
#     return ans


@njit(nopython = True)
def _numba_mean(t_L, t_R, v_R, shift_t, shift_k, win_k, is_time):
    is_cur = 0
    n_L, n_R = len(t_L), len(t_R)
    ans = np.zeros(n_L, dtype = np.float64)
        
    ans_i, cnt_nan, p1, p2 = 0, 0, 0, -1 # init status
    for pL in range(n_L):
        # ==================================================
        # get_p2
        p2_next = p2 + shift_k + 1
        while p2_next < 0 or (p2_next < n_R and t_L[pL] - shift_t >= t_R[p2_next]):
            if is_cur ==  1 and p2_next > pL: break
            
            # move p2
            p2 += 1 
            p2_next = p2 + shift_k + 1
            
            # add v_R[p2]
            v2 = v_R[p2] if p2 < n_R else np.nan
            if np.isnan(v2):
                cnt_nan += 1
          
        # ==================================================
        #  get_p1
        while p1 < n_R and p1 <= p2:
            if is_time == 1:
                if t_L[pL] - shift_t - t_R[p1] + 1 <= win_k: break   
            else:
                if p2 - p1  + 1 <= win_k: break
            
            # remove v_R[p1]
            v1 = v_R[p1] if p1 < n_R else np.nan
            if np.isnan(v1):
                cnt_nan -= 1
            
            # move p1
            p1 += 1
        
        # ==================================================
        # get_value
        if p2 - p1  + 1 - cnt_nan <= 0:
            ans[pL] = np.nan
        else: 
            p2_end = p2 + 1 if p2 + 1 <= n_R else n_R
            ans[pL] = np.nanmean(v_R[p1: p2_end])  
    return ans


@njit(nopython = True)
def _numba_std(t_L, t_R, v_R, shift_t, shift_k, win_k, is_time):
    is_cur = 0
    n_L, n_R = len(t_L), len(t_R)
    ans = np.zeros(n_L, dtype = np.float64)
        
    ans_i, cnt_nan, p1, p2 = 0, 0, 0, -1 # init status
    for pL in range(n_L):
        # ==================================================
        # get_p2
        p2_next = p2 + shift_k + 1
        while p2_next < 0 or (p2_next < n_R and t_L[pL] - shift_t >= t_R[p2_next]):
            if is_cur ==  1 and p2_next > pL: break
            
            # move p2
            p2 += 1 
            p2_next = p2 + shift_k + 1
            
            # add v_R[p2]
            v2 = v_R[p2] if p2 < n_R else np.nan
            if np.isnan(v2):
                cnt_nan += 1
          
        # ==================================================
        #  get_p1
        while p1 < n_R and p1 <= p2:
            if is_time == 1:
                if t_L[pL] - shift_t - t_R[p1] + 1 <= win_k: break   
            else:
                if p2 - p1  + 1 <= win_k: break
            
            # remove v_R[p1]
            v1 = v_R[p1] if p1 < n_R else np.nan
            if np.isnan(v1):
                cnt_nan -= 1
            
            # move p1
            p1 += 1
        
        # ==================================================
        # get_value
        if p2 - p1  + 1 - cnt_nan <= 0:
            ans[pL] = np.nan
        else: 
            p2_end = p2 + 1 if p2 + 1 <= n_R else n_R
            ans[pL] = np.nanstd(v_R[p1: p2_end])  
    return ans

@njit(nopython = True)
def _numba_min(t_L, t_R, v_R, shift_t, shift_k, win_k, is_time):
    is_cur = 0
    n_L, n_R = len(t_L), len(t_R)
    ans = np.zeros(n_L, dtype = np.float64)
        
    ans_i, cnt_nan, p1, p2 = 0, 0, 0, -1 # init status
    for pL in range(n_L):
        # ==================================================
        # get_p2
        p2_next = p2 + shift_k + 1
        while p2_next < 0 or (p2_next < n_R and t_L[pL] - shift_t >= t_R[p2_next]):
            if is_cur ==  1 and p2_next > pL: break
            
            # move p2
            p2 += 1 
            p2_next = p2 + shift_k + 1
            
            # add v_R[p2]
            v2 = v_R[p2] if p2 < n_R else np.nan
            if np.isnan(v2):
                cnt_nan += 1
          
        # ==================================================
        #  get_p1
        while p1 < n_R and p1 <= p2:
            if is_time == 1:
                if t_L[pL] - shift_t - t_R[p1] + 1 <= win_k: break   
            else:
                if p2 - p1  + 1 <= win_k: break
            
            # remove v_R[p1]
            v1 = v_R[p1] if p1 < n_R else np.nan
            if np.isnan(v1):
                cnt_nan -= 1
            
            # move p1
            p1 += 1
        
        # ==================================================
        # get_value
        if p2 - p1  + 1 - cnt_nan <= 0:
            ans[pL] = np.nan
        else: 
            p2_end = p2 + 1 if p2 + 1 <= n_R else n_R
            ans[pL] = np.nanmin(v_R[p1: p2_end])  
    return ans

@njit(nopython = True)
def _numba_max(t_L, t_R, v_R, shift_t, shift_k, win_k, is_time):
    is_cur = 0
    n_L, n_R = len(t_L), len(t_R)
    ans = np.zeros(n_L, dtype = np.float64)
        
    ans_i, cnt_nan, p1, p2 = 0, 0, 0, -1 # init status
    for pL in range(n_L):
        # ==================================================
        # get_p2
        p2_next = p2 + shift_k + 1
        while p2_next < 0 or (p2_next < n_R and t_L[pL] - shift_t >= t_R[p2_next]):
            if is_cur ==  1 and p2_next > pL: break
            
            # move p2
            p2 += 1 
            p2_next = p2 + shift_k + 1
            
            # add v_R[p2]
            v2 = v_R[p2] if p2 < n_R else np.nan
            if np.isnan(v2):
                cnt_nan += 1
          
        # ==================================================
        #  get_p1
        while p1 < n_R and p1 <= p2:
            if is_time == 1:
                if t_L[pL] - shift_t - t_R[p1] + 1 <= win_k: break   
            else:
                if p2 - p1  + 1 <= win_k: break
            
            # remove v_R[p1]
            v1 = v_R[p1] if p1 < n_R else np.nan
            if np.isnan(v1):
                cnt_nan -= 1
            
            # move p1
            p1 += 1
        
        # ==================================================
        # get_value
        if p2 - p1  + 1 - cnt_nan <= 0:
            ans[pL] = np.nan
        else: 
            p2_end = p2 + 1 if p2 + 1 <= n_R else n_R
            ans[pL] = np.nanmax(v_R[p1: p2_end])  
    return ans    

_numba_func_dict = {
    'merge_roll_sum': _numba_sum,
    'merge_roll_mean': _numba_mean,
    'merge_roll_std': _numba_std,
    'merge_roll_min': _numba_min,
    'merge_roll_max': _numba_max,
}

@njit(nopython=True, parallel=True)
def _numba_agg(op_func, 
               t_left, t_right, v_right, shift_t, shift_k, win_k, is_time,
               idx_all_L, idx_all_p1p2_L, idx_all_R, idx_all_p1p2_R):
    
    ans = np.zeros(len(t_left), dtype = np.float32)
    for i in numba.prange(0, len(idx_all_p1p2_L) - 1):
        idx_L = idx_all_L[idx_all_p1p2_L[i]: idx_all_p1p2_L[i + 1]]
        idx_R = idx_all_R[idx_all_p1p2_R[i]: idx_all_p1p2_R[i + 1]]
        ans[idx_L] = op_func(t_left[idx_L], t_right[idx_R], v_right[idx_R],
                             shift_t, shift_k, win_k, is_time)  
    return ans

def get_idx_all(idx_list):
    n = len(idx_list)
    idx_all_p1p2 = np.zeros(n + 1).astype(np.uint32)
    for i in range(n):
        idx_all_p1p2[i + 1] = idx_all_p1p2[i] + len(idx_list[i])
    idx_all = np.hstack(idx_list).astype(np.uint32)
    return idx_all, idx_all_p1p2

import datetime
def time_str():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def OP_merge_master(
        df_L, keys_L, col_time_L,
        df_R, keys_R, col_time_R,
        col, op, win_k,
        idx_all_DICT, idx_all_p1p2_DICT, a_keys_DICT,
        name_L = 'df_L', name_R = 'df_R',
        shift_t = 0, shift_k = 0
    ): 
    # partition
    # L
    if name_L not in idx_all_p1p2_DICT:
        print(f' ------------------------- {name_L} ------------------------- ')
        df_gp = df_L.groupby(keys_L).groups().to_numpy()
        a_keys = df_gp[:,:len(keys_L)]
        a_keys_DICT[name_L] = a_keys
        idx_list = df_gp[:,len(keys_L)]
        idx_all, idx_all_p1p2 = get_idx_all(idx_list)
        idx_all_DICT[name_L] = idx_all
        idx_all_p1p2_DICT[name_L] = idx_all_p1p2
        idx_all_L, idx_all_p1p2_L = idx_all, idx_all_p1p2
    else:
        idx_all_L, idx_all_p1p2_L = idx_all_DICT[name_L], idx_all_p1p2_DICT[name_L]

    # R
    if name_R not in idx_all_p1p2_DICT:
        print(f' ------------------------- {name_R} ------------------------- ')
        df_gp = df_R.groupby(keys_R).groups().to_numpy()
        a_keys = df_gp[:,:len(keys_R)]
        a_keys_DICT[name_R] = a_keys
        idx_list = df_gp[:,len(keys_R)]
        idx_all, idx_all_p1p2 = get_idx_all(idx_list)
        idx_all_DICT[name_R] = idx_all
        idx_all_p1p2_DICT[name_R] = idx_all_p1p2    
        idx_all_R, idx_all_p1p2_R = idx_all, idx_all_p1p2
    else:
        idx_all_R, idx_all_p1p2_R = idx_all_DICT[name_R], idx_all_p1p2_DICT[name_R]

    # value
    t_left = df_L[col_time_L].to_numpy()
    t_right = df_R[col_time_R].to_numpy()
    v_right = df_R[col].to_numpy().astype(np.float32)  
    
    # interpret win_k
    if type(win_k) == str:
        if win_k[-1] == 'M':
            win_k = f'{win_k[:-1]}n'
        unit_dict = {'s': 1, 'm': 60, 'h': 3600, 'd': 3600 * 24, 
                     'w': 3600 * 24 * 7, 'n': 3600 * 24 * 30, 'y': 3600 * 24 * 365}
        win_k = win_k.lower()
        unit = win_k[-1]
        win_k = int(win_k[:-1])
        win_k *= unit_dict[unit]
        is_time = 1
    else:
        win_k = int(win_k)
        is_time = 0

    # go    
    s = _numba_agg(_numba_func_dict[op],
               t_left, t_right, v_right, shift_t, shift_k, win_k, is_time,
               idx_all_L, idx_all_p1p2_L, idx_all_R, idx_all_p1p2_R) 
    return s