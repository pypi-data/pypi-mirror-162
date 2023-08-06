import os
import datetime
import time
import numpy as np
import pandas as pd
import polars as pl
from tqdm.notebook import tqdm
from .er.idxer import Idxer
from .er.namer import Namer
from .er.masker import Masker
from .er.scaler import Scaler
from .op.OPMaster import OPMaster
from ..util.util import get_mem_cur, get_mem_max, dump_dm

class DataMaster:
    # ============================== intit ==========================
    def __init__(self,
                 verbose=False,
                 keep_space=False,
                 dtype='float32'):
        self.verbose = verbose
        self.keep_space = keep_space
        self.dtype = dtype
        self.time_dict = {}
        self.time_list = []
        
        self.df_dict = {}
        self.idxer = Idxer()
        self.namer = Namer(verbose=verbose, keep_space=keep_space)
        self.masker = Masker()
        self.scaler = Scaler()
        self.OPMaster = OPMaster
        
    def __init__df(self, df_name):
        if df_name not in self.df_dict.keys():
            self.df_dict[df_name] = pl.DataFrame()
    
    # ============================== I/O ==========================
    def dump(self, path, drop = True):
        dump_dm(self, path, drop)
    
    # ============================== basic ==========================
    def show_all_info(self):
        print(f'[+] time_dict = \n{pd.Series(self.time_dict).sort_values()[::-1].head(30).to_string()}')
        print(f'[+] time_mean = {np.mean(self.time_list):.2f}')
        print(f'[+] shape = \n{self.shape()}')
        print(f'[+] dtypes_vc = \n{self.dtypes_vc().to_string()}')
        get_mem_cur()
        get_mem_max()

    def shape(self):
        shape_dict = {}
        for key in self.df_dict:
            shape_dict[key] = self.df_dict[key].shape
        return shape_dict

    def head(self, n=10, df_name='T0'):
        return self.df_dict[df_name][:n]

    def tail(self, n=10, df_name='T0'):
        return self.df_dict[df_name][-n:]    

    def dtypes(self, df_name='T0'):
        return self.head(df_name = df_name).to_pandas().dtypes

    def dtypes_vc(self, df_name='T0'):
        return self.dtypes(df_name = df_name).value_counts()

    def get_name_list_sel(self, name_list):
        dtypes_dict = self.dtypes().to_dict()
        name_list_sel = []
        for x in name_list:
            name_old = x
            if 'mask=' not in x.replace(' ', '') and '=' in x:
                name_old = x.split("=")[0].strip()
            dtype_str = str(dtypes_dict[name_old])
            if 'int' in dtype_str or 'float' in dtype_str:
                name_list_sel.append(name_old)
        return name_list_sel
    
    def sort_values(self, by, reverse, df_name = 'T0'):
        print(f'[+] sort_values, by = {by}, reverse = {reverse}')
        self.df_dict[df_name] = self.df_dict[df_name].sort(by = by, reverse = reverse)

    def is_same(self, c1, c2, df_name = 'T0'):
        dd = self.df_dict[df_name]
        v1, v2 = dd[c1].to_pandas(), dd[c2].to_pandas()
        idx = (v1 != v2)
        n_diff = (~v1.loc[idx].isnull()).sum() + (~v2.loc[idx].isnull()).sum()
        return n_diff == 0    
    
    # ============================== drop =====================
    def exist(self, col, df_name = 'T0'):
        if col in self.df_dict[df_name].columns:
            return True
        if col in self.namer.name_dict_all:
            return True
        return False

    def drop(self, cols, df_name='T0', verbose = True):
        if type(cols) != list:
            cols = [cols]
        
        for i, col in enumerate(cols):
            if self.namer.name_exist.get(col, False):
                if col in self.namer.name_dict_all:
                    col_new = self.namer.name_dict_all[col]['name_new']
                    col_new = col_new if col_new is not None else col
                    _ = self.df_dict[df_name].drop_in_place(col_new)
                else:
                    _ = self.df_dict[df_name].drop_in_place(col)
                self.namer.name_exist[col] = False
                if verbose:
                    print(f'[-][{i+1:04.0f}] {df_name}.{col}')

    # ============================== set and get =====================
    def set_mask(self, mask, mask_name):
        mask = mask.ravel()
        self.masker.mask_DICT[mask_name] = mask
        self.masker.idx_DICT[mask_name] = np.arange(len(mask))[mask == 1]

    def set_by_col(self, col, x, df_name='T0'):
        self.__init__df(df_name)
        self.df_dict[df_name][col] = x

    def set_by_df(self, df, df_name='T0', mask_name=None):
        self.__init__df(df_name)
        for col in df.columns:
            if self.dtype == 'float32':
                if str(df[col].dtype) == 'float64':
                    self.df_dict[df_name][col] = df[col].astype('float32')
                elif str(df[col].dtype) == 'int64':
                    self.df_dict[df_name][col] = df[col].astype('int32')
                else:
                    self.df_dict[df_name][col] = df[col]
            else:
                self.df_dict[df_name][col] = df[col]

    def get_col_pandas(self, col, df_name='T0', mask_name=None):
        if mask_name is not None:
            mask_DICT, idx_DICT = self.masker.get_DICT()
            return self.df_dict[df_name][col].to_pandas().iloc[idx_DICT[mask_name]]
        return self.df_dict[df_name][col].to_pandas()

    def get_col_numpy(self, col, df_name='T0', mask_name=None):
        if mask_name is not None:
            mask_DICT, idx_DICT = self.masker.get_DICT()
            return self.df_dict[df_name][col].to_numpy()[idx_DICT[mask_name]]
        return self.df_dict[df_name][col].to_numpy()

    def get_col_polars(self, col, df_name='T0', mask_name=None):
        if mask_name is not None:
            mask_DICT, idx_DICT = self.masker.get_DICT()
            return self.df_dict[df_name][col].to_numpy()[idx_DICT[mask_name]]
        return self.df_dict[df_name][col]

    def get_cols_pandas(self, cols=None, df_name='T0', mask_name=None):
        if cols is None:
            cols = list(self.df_dict[df_name].columns)
        if mask_name is not None:
            mask_DICT, idx_DICT = self.masker.get_DICT()
            return self.df_dict[df_name][cols].to_pandas().iloc[idx_DICT[mask_name]]
        return self.df_dict[df_name][cols].to_pandas()

    def get_cols_numpy(self, cols=None, df_name='T0', mask_name=None):
        if cols is None:
            cols = list(self.df_dict[df_name].columns)
        if mask_name is not None:
            mask_DICT, idx_DICT = self.masker.get_DICT()
            return self.df_dict[df_name][cols].to_numpy()[idx_DICT[mask_name]]
        return self.df_dict[df_name][cols].to_numpy()

    def get_cols_polars(self, cols=None, df_name='T0', mask_name=None):
        if cols is None:
            cols = list(self.df_dict[df_name].columns)
        if mask_name is not None:
            mask_DICT, idx_DICT = self.masker.get_DICT()
            return self.df_dict[df_name][cols][idx_DICT[mask_name]]
        return self.df_dict[df_name][cols]

    def get_cur_fe(self):
        return list(self.namer.name_dict_all.keys())

    # ============================== FE ==============================
    # fe_gogogo
    def fe_go(self, name_list, keep_name = False, verbose = True):
        # ---------- name_list_2_dict ----------
        name_dict = self.namer.name_list_2_dict(name_list)
        # self.namer.show_name_list(name_list)
        # self.namer.show_name_dict(name_dict)

        # ---------- dict_2_fe -----------------
        fe_list = []
        self.namer.dict_2_fe(name_dict, fe_list)

        # ---------- memory all -----------------
        if len(name_dict) > 0:
            self.namer.name_dict_last = {**name_dict} 
            self.namer.name_dict_all = {**self.namer.name_dict_all, **name_dict}
        if len(fe_list) > 0:
            self.namer.fe_list_last = fe_list[:]
            self.namer.fe_list_all.extend(fe_list)

        # ---------- fe_generator --------------
        if verbose:
            print(f'[+] total = {len(fe_list)}')
        for fe in fe_list:
            name = fe["name"]
            self.namer.name_exist[name] = False
        
        
        rg = enumerate(fe_list)
        if verbose:
            rg = tqdm(enumerate(fe_list), desc='fe_generator', total=len(fe_list))
        for ti, fe in rg:
            name = fe["name"]
            # time_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            # time_str = datetime.datetime.now().strftime("%H:%M:%S")
            # print(f'[{time_str}][{ti + 1:04}] {name.ljust(70)}', end = '')
            # logger.info(f'[{ti + 1:04}] {name}')

            if verbose:
                print(f'[{ti + 1:04}] {name.ljust(90)}', end='')
            t1 = time.time()
            self.OPMaster.fe_generator(self, fe, keep_name)
            self.namer.name_exist[name] = True
            t2 = time.time()
            if verbose:
                print(f'time = {t2 - t1:0.2f}')
            self.time_list.append(t2 - t1)
            self.time_dict[name] = t2 - t1
        self.time_list = self.time_list
