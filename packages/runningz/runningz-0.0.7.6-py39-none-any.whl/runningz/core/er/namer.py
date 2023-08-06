import numpy as np
import pandas as pd
import polars as pl
from fractions import Fraction

class Namer:
    def __init__(self, verbose=False, keep_space=False):
        self.cnt = 0
        self.verbose = verbose
        self.keep_space = keep_space
        self.name_exist = {}

        self.name_dict_all = {}
        self.fe_list_all = []

    def show_name_list(self, name_list):
        import json
        print('\n'.join(name_list))

    def show_name_dict(self, name_dict):
        import json
        print(json.dumps(name_dict, indent=4)) 

    def name_list_2_dict(self, name_list):
        name_dict = {}
        for name in name_list:
            name = name.strip()
            if not self.keep_space:
                # not use this to keep ' '
                name = name.replace(' ', '')
            name, ans = self.name_2_dict(name)  # strip()
            if len(ans) == 0: # origin col
                continue
            name_dict[name] = ans
        return name_dict

    def dict_2_fe(self, name_dict, fe_list):
        self.dict_2_fe(name_dict, fe_list)
        return fe_list

    # ==================== name str to dict ====================
    def get_match_idx(self, s, p2):
        p2 += 1
        stack = []
        while p2 < len(s):
            if s[p2] == '(':
                stack.append('(')
            elif s[p2] == ')':
                if len(stack) == 0:
                    return p2
                else:
                    stack.pop()
            p2 += 1
        return -1

    def get_args(self, s):
        # if ',' not in s:
        #     return [s]

        args = []
        p1, p2 = 0, 0
        while p2 < len(s):
            if s[p2] == ',':
                args.append(s[p1: p2])
                p1 = p2 + 1
                p2 = p2 + 2
            elif s[p2] == '(':
                p2 = self.get_match_idx(s, p2)  # idx of the match ')'
                assert p2 >= 0, f'{s} not valid! not match ()'

                name = s[p1: p2+1]
                name = name.strip()
                name, ans = self.name_2_dict(name) # strip()
                args.append({name: ans})  
                p1 = p2 + 2
                p2 = p2 + 3
            else:
                p2 += 1
        if p1 < len(s):
            args.append(s[p1:p2])
        return args

    def str_2_number(self, s):
        if type(s) != str:
            return s
        try:
            s = int(s)
        except:
            try:
                s = float(s)
            except:
                try:
                    s = float(Fraction(s.replace(' ', '')))
                except:
                    pass
                
        return s

    def name_2_dict(self, name):
        if '(' not in name:
            return name, {}

        ans = {}
        while True:
            idx = name.index('(')
            assert name[-1] == ')', f'{name} not valid! not match ()'
            if idx > 0:
                break
            else:
                name = name[1:-1] # op(((n1))) -> op(n1)

        # op
        op = name[:idx]
        ans['op'] = op
        # name_new=Ti.op(...)
        if '=' not in op:
            name_new = None
        else:
            i = op.index('=')
            name_new, op = op[:i].strip(), op[i + 1:].strip()
        ans['name_new'] = name_new
        ans['op'] = op

        # args
        ans['args'] = self.get_args(name[idx + 1: -1])
        ans['args'] = [self.str_2_number(s) for s in ans['args']]
        return name, ans

    # ==================== name_dict to generate fe ====================
    def dict_2_fe(self, name_dict, fe_list):
        for name in name_dict:
            if self.name_exist.get(name, False):
                # print(f'[-] {name}, exist')
                # print('')
                continue
            self.name_exist[name] = True

            if type(name_dict[name]) is str:
                if self.verbose:
                    print(f'[o][{0:04d}] {name} -> origin')
                continue

            op = name_dict[name]['op']
            args = name_dict[name]['args']
            _ = [self.dict_2_fe(x, fe_list) for x in args if type(x) is dict]
            args_ready = [x if type(x) is not dict else list(
                x.keys())[0] for x in args]

            # strip()
            op = op.strip()
            args_ready = [x.strip() if type(
                x) is str else x for x in args_ready]

            # Ti.op(...)
            if '.' not in op:
                df_name = 'T0'
            else:
                i = op.rindex('.')
                df_name, op = op[:i], op[i + 1:]

            #  -------------------- call FE, begin --------------------
            if self.verbose:
                print(f'[+][{self.cnt + 1:04d}] {name}')
            fe_list.append({'name': name, 'name_new': name_dict[name]['name_new'],
                            'df_name': df_name, 'op': op, 'args': args_ready})
            self.cnt += 1
            # args_str = ",".join([f'\"{x}\"' if type(x) is str else str(x) for x in args_ready])
            # print(f'    {op}({args_str})')
            #  -------------------- call FE, end   --------------------
