import numpy as np
import pandas as pd
import polars as pl
import hashlib
import chinese_calendar

class OP_other:
    # ---------------------------------------- info ------------------------------------------
    # usable op
    op_list = [
        'date_int',
        'to_datetime',
        'timestamp',
        'date_str',
        'dow',
        'weekend',
        'holiday',
        'year',
        'month',
        'day',

        'days_diff',
        'seconds_diff',
        'substr',
    ]

    # example
    name_list = [
        'date_int(date)',
        'date_t = to_datetime(date_int(date))',
        'ts = timestamp(date_t)',
        'date_str(date_t)',
        'date_str(date)',
        
        'dow(date_t)',
        'weekend(date_t)',
        'holiday(date_t)',
        'year(date_t)',
        'month(date_t)',
        'day(date_t)',
        
        'days_diff(date_t, 2010-01-01)',
        'seconds_diff(date_t, 2010-01-01)',
        'substr(date_str(date_t), 0, 10)',
    ]

    # ---------------------------------------- op(s) ----------------------------------------
    # datetime
    def date_int(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.apply(lambda x: int(str(x)[:10].replace('-', ''))).values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)
        
        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.apply(lambda x: int(str(x)[:10].replace('-', ''))).values
        df_kv = pl.DataFrame({'k':k.astype(str), 'v': v.astype(np.int32)})
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    def date_str(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            if s.dtypes == object:
                v = s2.apply(lambda x: str(x)[:10]).values
            else:
                v = s2.dt.date.astype(str)
            kv = dict(zip(k, v))
            return s.map(kv)
        
        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        if s2.dtypes == object:
            v = s2.apply(lambda x: str(x)[:10]).values
        else:
            v = s2.dt.date.astype(str)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']  
        return ans  

    def to_datetime(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            if 'int' in str(s.dtypes):
                v = pd.to_datetime(s2, format='%Y%m%d').values
            else:
                v = pd.to_datetime(s2).values
            kv = dict(zip(k, v))
            return s.map(kv)
        
        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        if 'int' in str(s2.dtypes):
            v = pd.to_datetime(s2, format='%Y%m%d').values
        else:
            v = pd.to_datetime(s2).values
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    def timestamp(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = (s2 - pd.to_datetime('1970-01-01')).dt.total_seconds().values.astype(np.int32) - 8 * 3600
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = (s2 - pd.to_datetime('1970-01-01')).dt.total_seconds().values.astype(np.int32) - 8 * 3600
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    def dow(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.dayofweek.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.dt.dayofweek.values.astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans
    
    def weekend(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.dayofweek.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = (s2.dt.dayofweek.values >= 5).astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    def holiday(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.dayofweek.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.map(chinese_calendar.is_holiday)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans        

    def year(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.year.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.dt.year.values.astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    def month(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.month.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.dt.month.values.astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    def day(s):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.day.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.dt.day.values.astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    # ---------------------------------------- op(s0, s1) ----------------------------------------
    def days_diff(s0, s1):
        if type(s1) == str:
            s1 = pd.to_datetime(s1)
        elif 'int' in str(s1.dtypes):
            s1 = pd.to_datetime(s1, format='%Y%m%d')
        if type(s0) == pd.Series:
            s = pl.Series((s0 - s1))
        else:
            s = pl.Series((s0.to_pandas() - s1))

        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.days.values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)
        
        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.dt.days.values.astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans


    def seconds_diff(s0, s1):
        if type(s1) == str:
            s1 = pd.to_datetime(s1)
        elif 'int' in str(s1.dtypes):
            s1 = pd.to_datetime(s1, format='%Y%m%d')
        if type(s0) == pd.Series:
            s = pl.Series((s0 - s1))
        else:
            s = pl.Series((s0.to_pandas() - s1))

        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.dt.total_seconds().values
            kv = dict(zip(k, v))
            return s.map(kv).astype(np.int32)
        
        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.dt.total_seconds().values.astype(np.int32)
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans

    # ---------------------------------------- op(s, i, j) ----------------------------------------
    # str
    def substr(s, i, j):
        if type(s) == pd.Series:
            s2 = s.drop_duplicates()
            k = s2.values
            v = s2.str[i:j]
            kv = dict(zip(k, v))
            return s.map(kv)

        s = s.to_frame(); s.columns = ['k']
        s2 = s.distinct(subset = 'k')['k'].to_pandas()
        k = s2.values
        v = s2.str[i:j]
        df_kv = pl.DataFrame(pd.DataFrame({'k': k, 'v': v}))
        ans = s.join(df_kv, on = 'k', how = 'left')['v']
        return ans