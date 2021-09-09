import pandas as pd
import pingouin as pt

pd.set_option('display.float_format', '{:.3f}'.format)

"""進行 t 檢定"""
def ttest(group, data1, data2, item1 = 'player.wtp_voting_cost', item2 = 'player.wtp_voting_cost_pq', completed = False, paired = True):
    
    if (completed == False):
        result = pt.ttest(data1[item1], data2[item2], paired = paired)
        p = result['p-val'].values[0]
        t = result['T'].values[0]
        summary = [{'沒門檻/有門檻': group, 'p-value':p, 't-statistic': t}]
        summary = pd.DataFrame(summary)

    else:
        summary = pt.ttest(data1[item1], data2[item2], paired = paired)

    return summary

"""計算 mean"""
def get_mean(group, data, item, colname):
    mean = data[item].describe()['mean']
    summary = [{'沒門檻/有門檻': group, colname: mean}]
    summary = pd.DataFrame(summary)
    return summary    