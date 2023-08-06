__author__ = 'Roy'

import pandas as pd


class csv:
    def __init__(self, csv_file):
        self.file = csv_file

    def to_df(self):
        return pd.read_csv(self.file)
