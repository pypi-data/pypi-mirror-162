import numpy as np
import pandas as pd
import polars as pl
import hashlib
from ._numba import OP_groupby_master
from ._numba_merge_roll import OP_merge_master


# ======================================== local util ========================================
def get_df_name_keys(df_name, keys):
    df_name_keys = f'{df_name}.{"__".join(keys)}'
    df_name_keys = df_name_keys.replace('(', '<').replace(')', '>').replace(',', '__')
    return df_name_keys   


def get_name_list_example():
    name_list = []
    for op in ['roll']:
        for _op in ['mean', 'std', 'min', 'max', 'sum']:
            for keys in ['c1', 'c2', 'c3', 'x(c1,c2)', 'x(c1,c3)', 'x(c2,c3)']:
                for col in ['n1','n2','n3', 'n4']:
                    for col_time in ['time']:
                        for k in [5,10,20,30,40,50,60]:
                            name = f'{op}({_op}, {keys}, {col}, {col_time}, {k})'
                            name_list.append(name)
    for op in ['merge']:
        for _op in ['mean', 'std', 'min', 'max', 'sum']:
            for keys in ['c1', 'c2', 'c3', 'x(c1,c2)', 'x(c1,c3)', 'x(c2,c3)']:
                for col in ['n1','n2','n3', 'n4']:
                    df_name = get_df_name_keys('T0', [keys])
                    name = f'{op}({df_name}, {keys}, {keys}, gp({_op}, {keys}, {col}))'
                    name_list.append(name) 
    for op in ['agg']:
        for _op in ['mean', 'std', 'min', 'max', 'sum']:
            for keys in ['c1', 'c2', 'c3', 'x(c1,c2)', 'x(c1,c3)', 'x(c2,c3)']:
                for col in ['n1','n2','n3', 'n4']:
                    name = f'{op}({_op}, {keys}, {col})'
                    name_list.append(name)    
                    name = f'{op}({_op}, {keys}, {col}, mask=train)'
                    name_list.append(name)    

    for op in ['merge_roll']:
        for _op in ['mean', 'std', 'min', 'max', 'sum']:
            for keys in ['c1']:
                for col in ['n1','n2','n3', 'n4']:
                    for k in [5,10,20,30,40,50,60]:
                        # f'merge_roll(sum, T0, c1, c1, time, time, n1, {i})'
                        name = f'{op}({_op}, T0, {keys}, {keys}, time, time, {col}, {k})'
                        name_list.append(name)                 
    return name_list


class OP_groupby:
    # ---------------------------------------- info ------------------------------------------
    # usable op
    op_list = [
        'x', 'roll', 'agg', 'gp', 'merge', 'merge_roll',
    ]
    # example
    name_list = get_name_list_example()
    # name_list += [
    #     'roll(ewm, c1, n1, time, 0.9)',
    #     'roll(shift, c1, n1, time, -2)',    

    #     'agg(rank, c1, n1)', 
    #     'agg(count, c1, c1)',
    #     'agg(nan, c1, n1)', 
    #     'agg(nonan, c1, n1)'
    # ]

    # ---------------------------------------- op(df_keys) ----------------------------------------
    def x(df_keys):
        def _hash(x):
            ans = int(hashlib.md5(x.__str__().encode()).hexdigest()[:7], 16)
            return ans

        keys = list(df_keys.columns)
        df_gp = df_keys.distinct(subset=keys)
        df_gp['__temp__'] = df_gp[keys].apply(_hash)['apply']
        ans = df_keys.join(df_gp, on=keys, how='left')['__temp__'].to_numpy()
        ans = ans.astype(np.int32)
        return ans

    # ---------------------------------------- op(...) ----------------------------------------
    def roll(df, keys, col, op, col_time, k, idx_all_DICT, idx_all_p1p2_DICT, df_name_keys, a_keys_DICT, mask):
        ans = OP_groupby_master(df, keys, col, op, col_time, k,
                                idx_all_DICT, idx_all_p1p2_DICT, df_name_keys, a_keys_DICT, mask)
        return ans
    gp = roll
    agg = roll

    def merge(df_L, df_R, left_on, right_on, col):
        ans = df_L.join(df_R, left_on, right_on, how='left')[col].to_numpy()
        return ans

    def merge_roll(df_L, keys_L, col_time_L,
                   df_R, keys_R, col_time_R,
                   col, op, win_k,
                   idx_all_DICT, idx_all_p1p2_DICT, a_keys_DICT,
                   name_L = 'df_L', name_R = 'df_R',
                   shift_t = 0, shift_k = 0):
        
        ans = OP_merge_master(
            df_L, keys_L, col_time_L,
            df_R, keys_R, col_time_R,
            col, op, win_k,
            idx_all_DICT, idx_all_p1p2_DICT, a_keys_DICT,
            name_L = name_L, name_R = name_R,
            shift_t = shift_t, shift_k = shift_k,
        )
        return ans 


