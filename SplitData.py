import pandas as pd

"""切割資料集"""
class splitData:
    def __init__(self, data):
        self.data = data

    """切割成 control, treatment"""
    def ct_split(self):
        control = self.data.loc[(self.data['treatment'] == 0)]
        treatment = self.data.loc[(self.data['treatment'] == 1)]
        return control, treatment

    """切割 bb, bb_same, bb_diff, bs, sb, ss"""
    def sb_split(self):
        bb = self.data.loc[(self.data['sb_condition'] == 'bb')]
        bb_same = self.data.loc[(self.data['bb_pq']) == 'same']
        bb_diff = self.data.loc[(self.data['bb_pq'] == 'different')]
        bs = self.data.loc[(self.data['sb_condition'] == 'bs')]
        sb = self.data.loc[(self.data['sb_condition'] == 'sb')]
        ss = self.data.loc[(self.data['sb_condition'] == 'ss')]
        return bb, bb_same, bb_diff, bs, sb, ss