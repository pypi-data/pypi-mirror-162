import numpy as np
import pandas as pd
import polars as pl
import warnings, time
warnings.filterwarnings('ignore')
import numba
from numba import njit
import scipy


@njit(nopython = True)
def _numba_2_diff_sum(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            ans_i = np.nansum(v1 - v2)
            ans[p2] = ans_i
    return ans


@njit(nopython = True)
def _numba_2_diff_abs_sum(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            ans_i = np.nansum(np.abs(v1 - v2))
            ans[p2] = ans_i
    return ans


@njit(nopython = True)
def _numba_2_diff_mean(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            ans_i = np.nanmean(v1 - v2)
            ans[p2] = ans_i
    return ans   


@njit(nopython = True)
def _numba_2_diff_abs_mean(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            ans_i = np.nanmean(np.abs(v1 - v2))
            ans[p2] = ans_i
    return ans       


@njit(nopython = True)
def _numba_2_corr(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # because this op have to fillnan
    for i in range(n):
        if np.isnan(a[i, 0]):
            a[i, 0] = 0
        if np.isnan(a[i, 1]):
            a[i, 1] = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            v1_mean = np.mean(v1)
            v2_mean = np.mean(v2)
            up = np.mean((v1 - v1_mean) * (v2 - v2_mean))
            dn = ((np.mean(v1 * v1) - v1_mean ** 2) * (np.mean(v2 * v2) - v2_mean ** 2)) ** 0.5
            if up == 0 or dn == 0:
                ans_i = v1_mean
            else:
                ans_i = up / dn
            ans[p2] = ans_i
    return ans     

@njit(nopython = True)
def _numba_2_beta(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # because this op have to fillnan
    for i in range(n):
        if np.isnan(a[i, 0]):
            a[i, 0] = 0
        if np.isnan(a[i, 1]):
            a[i, 1] = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            v1_mean = np.mean(v1)
            v2_mean = np.mean(v2)
            up = np.mean(v1 * v2) - (v1_mean * v2_mean)
            dn = np.mean(v2 * v2) - (v2_mean * v2_mean)
            if up == 0 or dn == 0:
                ans_i = v1_mean
            else:
                ans_i = up / dn
            ans[p2] = ans_i
    return ans  

@njit(nopython = True)
def _numba_2_alpha(a, k, is_time = 0):
    # dict
    n = len(a)
    cnt_nan = 0

    # because this op have to fillnan
    for i in range(n):
        if np.isnan(a[i, 0]):
            a[i, 0] = 0
        if np.isnan(a[i, 1]):
            a[i, 1] = 0

    # rolling 
    ans = np.zeros(n, dtype = np.float64)
    p1 = 0
    for p2 in range(n):
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
            ans[p2] = np.nan       
        else:
            v1 = a[p1: p2 + 1, 0]
            v2 = a[p1: p2 + 1, 1]
            v1_mean = np.mean(v1)
            v2_mean = np.mean(v2)
            up = np.mean(v1 * v2) - (v1_mean * v2_mean)
            dn = np.mean(v2 * v2) - (v2_mean * v2_mean)
            if up == 0 or dn == 0:
                ans_i = v1_mean
            else:
                ans_i = v1_mean - (up / dn) * v2_mean
            ans[p2] = ans_i
    return ans              


