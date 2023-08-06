import numpy as np
import pandas as pd
import polars as pl
import hashlib


class OP_2:
    # ---------------------------------------- info ------------------------------------------
    # usable op
    op_list = [
        'add', 'dif', 'mul', 'div', 'ddiv', 
        'min', 'max', 'ret', 'log_ret',
        'cmp', 'eq', 'ge', 'le', 'gt', 'lt', 
        '_and', '_or', '_xor', '_not',
    ]

    # example
    name_list = [
        'add(n1, n2)',
        'dif(n1, n2)',
        'mul(n1, n2)',
        'div(n1, n2)',
        'ddiv(n1, n2)',
        'min(n1, n2)',
        'max(n1, n2)',
        'ret(n1, n2)',
        'log_ret(n1, n2)',
        'cmp(n1, n2)',
        'eq(n1, n2)',
        'ge(n1, n2)',
        'le(n1, n2)',
        'gt(n1, n2)',
        'lt(n1, n2)',
        '_and(n3, n4)',
        '_or(n3, n4)',
        '_xor(n3, n4)',

        'add(n1, 1)',
        'dif(n1, 1)',
        'mul(n1, 1)',
        'div(n1, 1)',
        'ddiv(n1, 1)',
        'min(n1, 1)',
        'max(n1, 1)',
        'ret(n1, 1)',
        'log_ret(n1, 1)',
        'cmp(n1, 1)',
        'eq(n1, 1)',
        'ge(n1, 1)',
        'le(n1, 1)',
        'gt(n1, 1)',
        'lt(n1, 1)',
    ]
    
    # ---------------------------------------- op(x0,[x1,v]) ----------------------------------------
    def add(x0, x1):
        return (x0 + x1).astype(np.float32)

    def dif(x0, x1):
        return (x0 - x1).astype(np.float32)

    def mul(x0, x1):
        return (x0 * x1).astype(np.float32)

    def div(x0, x1):
        return (x0 / x1).astype(np.float32)

    def ddiv(x0, x1):
        return (x0 // x1).astype(np.float32)

    def min(x0, x1):
        ans = x0.copy()
        idx = x1 < x0
        if type(x1) == float or type(x1) == int:
            ans[idx] = x1
        else:
            ans[idx] = x1[idx]
        return ans

    def max(x0, x1):
        ans = x0.copy()
        idx = x1 > x0
        if type(x1) == float or type(x1) == int:
            ans[idx] = x1
        else:
            ans[idx] = x1[idx]
        return ans    
    
    def ret(x0, x1):
        return (x1 / x0 - 1).astype(np.float32)

    def log_ret(x0, x1):
        return (np.log(np.abs(x1)) - np.log(np.abs(x0))).astype(np.float32)

    # logi
    def cmp(x0, x1):
        return (x0 > x1).astype(np.int32)

    def eq(x0, x1):
        return (x0 == x1).astype(np.int32)

    def ge(x0, x1):
        return (x0 >= x1).astype(np.int32)

    def le(x0, x1):
        return (x0 <= x1).astype(np.int32)

    def gt(x0, x1):
        return (x0 > x1).astype(np.int32)

    def lt(x0, x1):
        return (x0 < x1).astype(np.int32)

    def _and(x0, x1):
        return (x0.astype(bool) & x1.astype(bool)).astype(np.int32)

    def _or(x0, x1):
        return (x0.astype(bool) | x1.astype(bool)).astype(np.int32)

    def _xor(x0, x1):
        return (x0.astype(bool) ^ x1.astype(bool)).astype(np.int32)    
