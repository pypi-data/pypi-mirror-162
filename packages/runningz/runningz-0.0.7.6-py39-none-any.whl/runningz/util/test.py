import time
import numpy as np
import pandas as pd
import numba
import psutil
from .util import set_numba_n_jobs
from ..core.DataMaster import DataMaster
from .. import api
from .util import get_mem_cur, get_mem_max

def test_performerce(n, n_jobs = -1, path = None):
    n = int(n)
    set_numba_n_jobs(n_jobs)
    # ---------------------------------------- test data ----------------------------------------
    np.random.seed(42)
    # n = int(5e6)
    # n = int(6e5)
    df = pd.DataFrame({
        'c1':np.random.randint(0, 5000, n).astype(np.int32),
        'c2': np.random.randint(0, 100, n).astype(np.int32),
        'c3': np.random.randint(0, 10, n).astype(np.int32),
        
        'time': np.random.permutation(n).astype(np.int32),
        'n1': np.random.random(n).astype(np.float32),
        'n2': np.random.random(n).astype(np.float32),
        'n3': np.random.randint(0, 2, n).astype(np.float32),
        'n4': np.random.randint(0, 2, n).astype(np.float32),
    })

    s = pd.date_range('20100101', '20201231')
    ss = pd.Series(s).dt.date.astype(str)
    ss = np.repeat(ss, len(df) // len(s) + 1)
    df['date'] = ss.values[np.random.permutation(len(ss))[:len(df)]]

    dm = DataMaster(verbose=False, keep_space=True)
    dm.set_by_df(df)
    dm.sort_values(['time', 'c1'], [False, False])
    mask = (df['c1'] < 1000).values
    dm.set_mask(mask, 'train')
    dm.show_all_info()

    # ---------------------------------------- fe_go ----------------------------------------
    name_list_1 = api.OP_1.name_list
    name_list_2 = api.OP_2.name_list
    name_list_m = api.OP_m.name_list
    name_list_other = api.OP_other.name_list
    name_list_groupby = api.OP_groupby.name_list
    np.random.random(42)
    name_list_groupby = list(np.random.permutation(name_list_groupby))[:1000]
    name_list_groupby = sorted(name_list_groupby)
    name_list = name_list_1 + name_list_2 + name_list_m + name_list_other + name_list_groupby
    print(f'name_list = {len(name_list)}')
    t1 = time.time()
    dm.fe_go(name_list)
    t2 = time.time()

    # ---------------------------------------- log_abs ----------------------------------------
    name_list_sel = dm.get_name_list_sel(name_list)
    name_list_log_abs = [f'numba_log_abs({x})' for x in name_list_sel]
    print(f'name_list_log_abs = {len(name_list_log_abs)}')
    t3 = time.time()
    dm.fe_go(name_list_log_abs, keep_name = True);
    t4 = time.time()

    # ---------------------------------------- zscore_v ----------------------------------------
    name_list_sel = dm.get_name_list_sel(name_list)
    name_list_log_abs = [f'zscore_v({x}, 0, 1)' for x in name_list_sel]
    t5 = time.time()
    dm.fe_go(name_list_log_abs, keep_name = True)
    t6 = time.time()
    
    dm.show_all_info()

    # time info
    print(f'[+] time_fe_all  = {t2 - t1}')
    print(f'[+] time_log_abs = {t4 - t3}')
    print(f'[+] time_zscore_v = {t6 - t5}')

    if path is not None:
        dm.dump(path)

    time.sleep(5)
    get_mem_cur()
    get_mem_max()
