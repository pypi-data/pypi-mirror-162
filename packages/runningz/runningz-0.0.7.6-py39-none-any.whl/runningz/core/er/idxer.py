import numpy as np
import pandas as pd
import polars as pl


class Idxer:
    def __init__(self):
        self.idx_all_DICT = {}
        self.idx_all_p1p2_DICT = {}

    def get_DICT(self):
        return self.idx_all_DICT, self.idx_all_p1p2_DICT
        