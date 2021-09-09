import pandas as pd
from statsmodels.formula.api import ols

pd.set_option('display.float_format', '{:.3f}'.format)


"""建立線性迴歸模型"""
class linearRegression:
    def __init__(self, formula, data):
        self.formula = formula
        self.data = data
        self.result = ols(formula, data).fit(cov_type='HC1')

    """得到迴歸模型結果"""
    def get_result(self, completed = False):
        # 只擷取下半部結果
        if completed == False:
            params = pd.DataFrame([dict(self.result.params)]).T
            std = pd.DataFrame([dict(self.result.bse)]).T
            t = pd.DataFrame([dict(self.result.tvalues)]).T
            p = pd.DataFrame([dict(self.result.pvalues)]).T
            conf = self.result.conf_int()
            summary = pd.concat([params, std, t, p, conf], axis = 1)
            summary.columns = ['Coef', 'Std err', 't-statistic', 'p-value', '[0.025', '0.975]']
        # 完整結果
        else:
            summary =  self.result.summary()

        return summary
    """"進行 F test, 並且得到結果"""
    def f_test(self, hypothesis = None):
        f = self.result.f_test(hypothesis).fvalue[0][0]
        p = self.result.f_test(hypothesis).pvalue
        p = p.round(3)
        summary = [{'Hypothesis':hypothesis, 'F-statistic': f, 'p-value': p}]
        summary = pd.DataFrame(summary)
        return summary

"""針對單一玩家建立模型, 可選擇是否要放交叉項"""
class single_player_lm:
    def __init__(self, wtp_data, interaction):
        self.wtp_data = wtp_data
        self.interaction = interaction

    def get_result(self):
    # 列出所有場次
        sessionList = self.wtp_data['session'].unique()
        # 存放結果
        result_df = []

        for session in sessionList:
            for playerID in range(1,16): 
                # 取子集
                subset = self.wtp_data.loc[(self.wtp_data['id'] == playerID) & (self.wtp_data['session'] == session)]
                # 建立迴歸模型
                if(self.interaction == True):
                    single_model = linearRegression(data = subset, formula = 'wtp ~ is_large + is_pq + is_large*is_pq')
                else:    
                    single_model = linearRegression(data = subset, formula = 'wtp ~ is_large + is_pq + is_large*is_pq')
                
                summary = single_model.result
                
                # 0: const, 1: is_large, 2: is_pq, 3: is_large*is_pq
                is_large = '+' if summary.params[1] > 0 else '-'
                is_pq = '+' if summary.params[2] > 0 else '-'
                p_is_large = summary.pvalues[1]
                p_is_pq = summary.pvalues[2]
                pList = [p_is_large, p_is_pq]
                
                if(self.interaction == True):
                    is_large_pq = '+' if summary.params[3] > 0 else '-'
                    p_is_large_pq = summary.pvalues[3]
                    pList = [p_is_large, p_is_pq, p_is_large_pq]
                
                sig = []

                for item in pList:
                    if (item < 0.001):
                        sig.append('***')
                    elif (item < 0.01):
                        sig.append('**')
                    elif (item < 0.05):
                        sig.append('*')
                    else:
                        sig.append('')
                
                if(self.interaction == True):
                    result_df.append({'session':session, 'playerID': playerID, 'is_large':is_large, 
                                    'sig_is_large':sig[0], 'is_pq':is_pq, 'sig_is_pq':sig[1], 
                                    'interaction':is_large_pq, 'sig_interaction':sig[2]}) 
                else:
                    result_df.append({'session':session, 'playerID': playerID, 'is_large':is_large, 
                                    'sig_is_large':sig[0], 'is_pq':is_pq, 'sig_is_pq':sig[1]})
        
        result_df = pd.DataFrame(result_df)
        
        return result_df

    def get_table(self):
        result_df = self.get_result()
        table_df = []

        # 統計人數 p: positive, n:negative
        pp = len(result_df.loc[((result_df['is_large'] == '+') & (result_df['is_pq'] == '+'))])
        pn = len(result_df.loc[((result_df['is_large'] == '+') & (result_df['is_pq'] == '-'))])
        np = len(result_df.loc[((result_df['is_large'] == '-') & (result_df['is_pq'] == '+'))])
        nn = len(result_df.loc[((result_df['is_large'] == '-') & (result_df['is_pq'] == '-'))])

        table_df.append({'is_large': '+', 'is_pq':'+', '人數': pp})
        table_df.append({'is_large': '+', 'is_pq':'-', '人數': pn})
        table_df.append({'is_large': '-', 'is_pq':'+', '人數': np})
        table_df.append({'is_large': '-', 'is_pq':'-', '人數': nn})

        table_df = pd.DataFrame(table_df)

        return table_df
