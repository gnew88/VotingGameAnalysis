import pandas as pd

def add_dummy(data):
    data['sb'] = data['sb_condition'].apply(lambda x : int(x == 'sb'))
    data['bb'] = data['sb_condition'].apply(lambda x : int(x == 'bb'))
    data['bs'] = data['sb_condition'].apply(lambda x : int(x == 'bs'))
    data['ss'] = data['sb_condition'].apply(lambda x : int(x == 'ss'))
    return data

class modify_wtp:
    def __init__(self, data):
        self.data = data

    """修改 control 資料集當中 wtp 計算方式"""
    def modify_control(self, mode = 'sum'):
        # 確保是使用 control 資料
        data = self.data.loc[(self.data['treatment'] == 0)]
        # 兩個選舉的 wtp 之和
        if mode == 'sum':
            data['wtp'] = data.apply(lambda x : x['player.wtp_voting_cost'] + x['player.wtp_voting_cost_pq'], axis = 1)
        if mode == 'min':
            data['wtp'] = data.apply(lambda x : min(x['player.wtp_voting_cost'], x['player.wtp_voting_cost_pq']), axis = 1)
        if mode == 'max':
            data['wtp'] = data.apply(lambda x : max(x['player.wtp_voting_cost'], x['player.wtp_voting_cost_pq']), axis = 1)
        if mode == 'pq':
            data['wtp'] = data['player.wtp_voting_cost_pq']
        if mode == 'no_pq':
            data['wtp'] = data['player.wtp_voting_cost']
        
        return data

    """將 treatment 的欄位改名為 wtp 以後, 與 control 合併"""
    def modify_all(self, mode):
        # 取得 control data 和 treatment data
        control_data = self.modify_control(mode)
        treatment_data = self.data.loc[(self.data['treatment'] == 1)]
        treatment_data.rename(columns = {'player.wtp_voting_cost':'wtp'}, inplace = True)
        data = pd.concat([control_data, treatment_data])
        return data