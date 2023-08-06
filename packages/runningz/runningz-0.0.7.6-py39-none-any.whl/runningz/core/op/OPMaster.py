import numpy as np
import pandas as pd
import polars as pl
from .op_1 import OP_1
from .op_2 import OP_2
from .op_m import OP_m
from .op_groupby import OP_groupby
from .op_other import OP_other
from .op_1_numba import OP_1_numba
from .op_m_numba import OP_m_numba


class OPMaster:
    def get_df_name_keys(df_name, keys):
        df_name_keys = f'{df_name}.{"__".join(keys)}'
        df_name_keys = df_name_keys.replace('(', '<').replace(')', '>').replace(',', '__')
        return df_name_keys   

    def get_zscore_vs(dm, df_name, name, vs):
        _mean, _std = vs
        key = f'{df_name}.{name}'
        scale_DICT = dm.scaler.get_DICT()
        if key not in scale_DICT.keys():
            scale_DICT[key] = {}
            x = dm.df_dict[df_name][name].to_numpy()
            if type(_mean) == str:
                _mean = np.nanmean(x)
            if type(_std) == str:
                _std = np.nanstd(x)
            _mean, _std = np.float32(_mean), np.float32(_std)
            scale_DICT[key]['mean'], scale_DICT[key]['std'] = _mean, _std
        else:
            _mean, _std = scale_DICT[key]['mean'], scale_DICT[key]['std']
        vs = _mean, _std
        return vs
    
    def fe_generator(dm, fe, keep_name = False):
        # use a simple name
        if fe['name_new'] is None:
            name = fe['name']
        else:
            name = fe['name_new']
        if keep_name:
            name = fe['args'][0] # keep name, use the first one of args
        df_name, op, args = fe['df_name'], fe['op'], fe['args']

        # ---------------------------------------- 1 ----------------------------------------
        if op in OP_1.op_list:
            c = args[0]
            vs = args[1:]
            if op in ['rank', 'rank_v']:
                x = dm.df_dict[df_name][c]
            else:
                x = dm.df_dict[df_name][c].to_numpy()

            # zscore with scaler
            if op in ['zscore_v']: 
                vs = OPMaster.get_zscore_vs(dm, df_name, name, vs)
            ans = eval(f'{OP_1.__name__}.{op}(x, *vs)')
            dm.set_by_col(name, ans, df_name)

        # ---------------------------------------- 1, numba ----------------------------------------
        elif op in OP_1_numba.op_list:
            _op = op
            c = args[0]
            vs = args[1:]
            x = dm.df_dict[df_name][c].to_numpy()
            idx_all_DICT, idx_all_p1p2_DICT = dm.idxer.get_DICT()
            ans = eval(f'{OP_1_numba.__name__}.numba_1(_op, x, df_name, idx_all_DICT, idx_all_p1p2_DICT, *vs)')
            dm.set_by_col(name, ans, df_name)    

        # ---------------------------------------- 2 ----------------------------------------
        elif op in OP_2.op_list:
            c0, c1 = args[0], args[1]
            x0, x1 = c0, c1
            if c0 in dm.df_dict[df_name].columns:
                x0 = dm.df_dict[df_name][c0].to_numpy()
            if c1 in dm.df_dict[df_name].columns:
                x1 = dm.df_dict[df_name][c1].to_numpy()
            ans = eval(f'{OP_2.__name__}.{op}(x0, x1)')
            dm.set_by_col(name, ans, df_name)

        # ---------------------------------------- m ----------------------------------------
        elif op in OP_m.op_list:
            # numpy
            if len(dm.df_dict[df_name]) <= 1e8:
                cs = args
                xs = dm.df_dict[df_name][cs].to_numpy()
                ans = eval(f'{OP_m.__name__}.{op}(xs)')
                dm.set_by_col(name, ans, df_name)
            # numpy
            else:
                _op = op
                cs = args
                x = dm.df_dict[df_name][cs].to_numpy().astype(np.float32)
                idx_all_DICT, idx_all_p1p2_DICT = dm.idxer.get_DICT()
                ans = eval(f'{OP_m_numba.__name__}.numba_m(_op, x, df_name, idx_all_DICT, idx_all_p1p2_DICT)')
                dm.set_by_col(name, ans, df_name)  

        # ---------------------------------------- other ----------------------------------------
        elif op in ['to_datetime', 'date_int', 'date_str', 'timestamp',
                     'dow', 'weekend', 'holiday', 'year', 'month', 'day']:
            c = args[0]
            if op in ['to_datetime', 'date_int', 'date_str', 'timestamp']:
                s = dm.df_dict[df_name][c]
            else:
                s = dm.df_dict[df_name][c].to_pandas()
            ans = eval(f'{OP_other.__name__}.{op}(s)')
            dm.set_by_col(name, ans, df_name)

        elif op in ['days_diff', 'seconds_diff']:
            c0, c1 = args[0], args[1]
            s0 = dm.df_dict[df_name][c0].to_pandas()
            s1 = c1
            if c1 in dm.df_dict[df_name].columns:
                s1 = dm.df_dict[df_name][c1].to_pandas()
            ans = eval(f'{OP_other.__name__}.{op}(s0, s1)')
            dm.set_by_col(name, ans, df_name)

        elif op in ['substr']:
            c, i, j = args
            s = dm.df_dict[df_name][c]
            ans = eval(f'{OP_other.__name__}.{op}(s, {i}, {j})')
            dm.set_by_col(name, ans, df_name)

        # ---------------------------------------- groupby ----------------------------------------
        # x
        elif op in ['x']:
            cs = args
            df_keys = dm.get_cols_polars(cs, df_name)
            ans = eval(f'{OP_groupby.__name__}.{op}(df_keys)')
            dm.set_by_col(name, ans, df_name)

        # roll, agg, gp
        elif op in ['roll', 'agg', 'gp']:
            # args
            col_time, k, mask = None, None, None
            if type(args[-1]) is str and '=' in args[-1]:
                mask = args[-1].split('=')[-1].strip()
                mask = dm.masker.mask_DICT[mask]
                args = args[:-1]

            # each op    
            col_2 = None
            df_name_gp = None
            if op == 'roll':
                if len(args) == 5:
                    _op, keys, col, col_time, k = args
                elif len(args) == 6:
                    _op, keys, col, col_2, col_time, k = args
            
            elif op == 'agg':
                _op, keys, col = args
            
            elif op == 'gp':
                if len(args) == 3:
                    _op, keys, col = args
                elif len(args) == 4:
                    _op, keys, col, df_name_gp = args # set df_name_gp, then gp need first before  roll or agg
            _op = f'{op}_{_op}'

            # dict
            keys = [keys]  # multi key had concat, [k1,k2] = x(k1,k2)
            df_name_keys = OPMaster.get_df_name_keys(df_name, keys)
            a_keys_DICT = {}
            idx_all_DICT, idx_all_p1p2_DICT = dm.idxer.get_DICT()
            groupby_done = df_name_keys in idx_all_DICT.keys()

            # cols_sel
            cols = [col] if col_2 is None else [col, col_2]
            if _op in ['agg_count', 'agg_nonan',  'agg_nan'] and keys[0] == col:
                cols_sel = keys
            elif col_time is None:
                cols_sel = keys + cols
            elif col_time in cols:
                cols_sel = keys + cols
            else:
                cols_sel = keys + cols + [col_time]

            # eval
            df = dm.get_cols_polars(cols_sel)
            ans = eval(f'{OP_groupby.__name__}.{op}(df, keys, cols, _op, col_time, k,\
                idx_all_DICT, idx_all_p1p2_DICT, df_name_keys, a_keys_DICT, mask)')

            #  new DataFrame, df_name_keys for gp
            if not groupby_done:
                df_keys = pd.DataFrame(a_keys_DICT[df_name_keys], columns=keys)
                dtypes_dict = dm.df_dict[df_name][:0][keys].to_pandas().dtypes.to_dict()
                df_keys = pl.DataFrame(df_keys.astype(dtypes_dict))
                dm.set_by_df(df_keys, df_name=df_name_keys if df_name_gp is None else df_name_gp)
            
            # ans
            df_name = df_name if op != 'gp' else (df_name_keys if df_name_gp is None else df_name_gp)
            dm.set_by_col(name, ans, df_name)
        
        # merge
        elif op in ['merge']:
            df_name_L = df_name
            df_name_R, left_on, right_on, col = args
            df_L = dm.get_cols_polars([left_on], df_name=df_name_L)
            df_R = dm.get_cols_polars([right_on, col], df_name=df_name_R)
            ans = eval(f'{OP_groupby.__name__}.{op}(df_L, df_R, left_on, right_on, col)')
            dm.set_by_col(name, ans, df_name)   

        elif op in ['merge_roll']:
            # 'T0.merge_roll(op, T1, c1, c1, t1, t1, n1, 10s, [shift_t, shift_k])'
            df_name_L = df_name
            shift_t, shift_k = 0, 0
            if len(args) == 8:
                _op, df_name_R, keys_L, keys_R, t_L, t_R, col, win_k = args
            elif len(args) == 9:
                _op, df_name_R, keys_L, keys_R, t_L, t_R, col, win_k, shift_t = args
            elif len(args) == 10:    
                _op, df_name_R, keys_L, keys_R, t_L, t_R, col, win_k, shift_t, shift_k = args
            _op = f'{op}_{_op}'

            keys_L, keys_R = [keys_L], [keys_R]
            name_L = OPMaster.get_df_name_keys(df_name_L, keys_L)
            name_R = OPMaster.get_df_name_keys(df_name_L, keys_R)
            
            df_L = dm.get_cols_polars(keys_L + [t_L], df_name = df_name_L)
            df_R = dm.get_cols_polars(keys_R + [t_R, col], df_name = df_name_R)
            idx_all_DICT, idx_all_p1p2_DICT = dm.idxer.get_DICT()
            a_keys_DICT = {}
            args_str = 'df_L, keys_L, t_L, df_R, keys_R, t_R,\
                        col, _op, win_k, idx_all_DICT, idx_all_p1p2_DICT, a_keys_DICT,\
                        name_L, name_R, shift_t, shift_k'
            ans = eval(f'{OP_groupby.__name__}.{op}({args_str})')

            #  new DataFrame, for gp
            if name_L not in dm.df_dict.keys():
                df_keys = pd.DataFrame(a_keys_DICT[name_L], columns=keys_L)
                dtypes_dict = dm.df_dict[df_name][:0][keys_L].to_pandas().dtypes.to_dict()
                df_keys = pl.DataFrame(df_keys.astype(dtypes_dict))
                dm.set_by_df(df_keys, df_name=name_L)
            if name_R not in dm.df_dict.keys():
                df_keys = pd.DataFrame(a_keys_DICT[name_R], columns=keys_R)
                dtypes_dict = dm.df_dict[df_name][:0][keys_R].to_pandas().dtypes.to_dict()
                df_keys = pl.DataFrame(df_keys.astype(dtypes_dict))
                dm.set_by_df(df_keys, df_name=name_R)    

            dm.set_by_col(name, ans, df_name)
        
        # ---------------------------------------- TODO ----------------------------------------
        else:
            assert False, f"{name}, [{op}] is not valid!"

