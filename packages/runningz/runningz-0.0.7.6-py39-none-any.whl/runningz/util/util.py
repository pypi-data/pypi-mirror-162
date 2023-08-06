import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
import numba
import psutil
import pickle
import resource
import polars as pl
import gc
import hashlib
import pytz
tz = pytz.timezone('Asia/Shanghai')

def rz_hash(x):
    ans = int(hashlib.md5(x.__str__().encode()).hexdigest()[:7], 16)
    return ans

# psutil
def set_numba_n_jobs(n_jobs = -1):
    cpus = psutil.cpu_count()
    if n_jobs <= 0 or n_jobs > cpus:
        n_jobs = cpus
    numba.set_num_threads(n_jobs)

def mem2str(mem):
    if mem // 1024 < 1:
        return '{:,.2f}B'.format(mem)
    if mem // (1024 * 1024)  < 1:
        return '{:,.2f}KB'.format(mem / 1024)
    if mem // (1024 * 1024 * 1024)  < 1:
        return '{:,.2f}MB'.format(mem / 1024 / 1024)
    
    return '{:,.2f}GB'.format(mem / 1024 / 1024 / 1024)        

def get_mem_cur():
    m = psutil.Process().memory_info().rss
    print(f'[+] mem_cur = {mem2str(m)} = {m:,.0f}')
    return m

def get_mem_max():
    m = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f'[+] mem_max = {mem2str(m)} = {m:,.0f}')
    return m    

# io
def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def dump_pickle(x, path):
    with open(path, 'wb') as f:
        pickle.dump(x, f)    

def load_dm(path):
    print(f'[+] path = {path}')
    dm = load_pickle(f'{path}/dm.rz')
    for df_name in dm.df_dict.keys():
        dm.df_dict[df_name] = pl.read_parquet(f'{path}/{df_name}.rz')
        print(f'[+] {path}/{df_name}.parquet, shape = {dm.df_dict[df_name].shape}')
    print('[+] load succ!')
    return dm

def dump_dm(dm, path, drop):
    print(f'[+] path = {path}')
    os.makedirs(path, exist_ok = True)
    for df_name in dm.df_dict.keys():
        print(f'[+] {path}/{df_name}.parquet, shape = {dm.df_dict[df_name].shape}')
        dm.df_dict[df_name].to_parquet(f'{path}/{df_name}.rz')
        if drop:
            dm.df_dict[df_name] = dm.df_dict[df_name][:0]
        gc.collect()
    dump_pickle(dm, f'{path}/dm.rz')
    print('[+] dump succ!')   



# ---------------------------------------- token for security ----------------------------------------
def rz_token(expired_date, k = 8):
    x = f'rz_{expired_date}'
    ans = hashlib.md5(x.__str__().encode()).hexdigest()[:8]
    ans += str(expired_date)
    return ans

def is_valid_token(token):
    if token is None:
        raise RuntimeError(f'[+] please set as, export rz_token=<your token>;')
    
    expired_date = str(token)[-8:]
    if rz_token(expired_date) != token:
        raise RuntimeError(f'[+] your token = {token} is not valid, please concat zhongrunxing@qq.com')
    
    today_str = datetime.datetime.now(tz).strftime('%Y%m%d')
    t_today = datetime.datetime.strptime(today_str, '%Y%m%d')
    t_expired = datetime.datetime.strptime(expired_date, '%Y%m%d')
    days = (t_expired - t_today).days

    if days < 0:
        raise RuntimeError(f'[+] your token = {token} is expired {abs(days)} ago, please concat zhongrunxing@qq.com')
        
    if days < 30:
        print(f'[+] your token = {token} has only {days} days, please concat zhongrunxing@qq.com')
    return True
# -----------------------------------------------------------------------------------------------------