__version__ = '0.0.7.6'
__author__ = 'runningz'
__descibe__ = 'fastmath=False'

import os
from numpy import argsort
from .core.api import DataMaster, OPMaster
from .util.api import *
from . import api

# token
is_valid_token(os.environ.get('rz_token'))

# ---------------------------------------- cmd ----------------------------------------
import sys
def test_runningz():
    print(f'[+] __version__ = {__version__}')

    if len(sys.argv) == 1:
        print('[+] hello runningz')
        return
    
    print(f'[+] sys.argv = {sys.argv}')   
    if sys.argv[1] != '--test':
        print('[+] hello runningz. only suport --test')
        return
    
    n_jobs = -1
    path = None
    if len(sys.argv) == 2:
        n = int(6e5)
    elif len(sys.argv) == 3:
        n = sys.argv[2]
        n = int(float(n))
    elif len(sys.argv) == 4:
        n = sys.argv[2]
        n = int(float(n))
        n_jobs = int(sys.argv[3])
    elif len(sys.argv) == 5:
        n = sys.argv[2]
        n = int(float(n))
        n_jobs = int(sys.argv[3])
        path = sys.argv[4]
    test_performerce(n, n_jobs, path)

