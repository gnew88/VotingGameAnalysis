import pandas as pd
import streamlit as st
from docx import Document
from DataProcessing import dataProcessing, mergingData
from Ttest_and_Mean import ttest, get_mean
from SplitData import splitData
from LinearRegression import linearRegression, single_player_lm
from DownloadData import download_link, get_binary_file_downloader_html
from ModifyData import add_dummy, modify_wtp
from ReportGenerator import reportGenerator

pd.set_option('display.float_format', '{:.3f}'.format)

st.title('Data Analysis for Voting Game')
st.info(' - 0902 以後的資料公投門檻設定為 25 % \n - 注意上傳的資料表末不得有多餘空白欄位')

st.markdown('---')

st.header('資料處理與合併')
# 注意事項
st.markdown('- 將資料轉換為場次-玩家-回合形式')
st.markdown('- sb_condition 表示在沒門檻/有門檻選舉中是小組 (small) 還是大組 (big)')
st.markdown('- bb_pq 紀錄在大大組的情形下，隊友立場與他相同 (same) 還是不同 (different)')

# 資料上傳
originalData = st.file_uploader('', accept_multiple_files = True, type = ['csv'])

files = []
for file in originalData:
    files.append(file.name)

if len(originalData) != 0:
    try:
        # 處理與合併所有原始資料
        merge_data = mergingData(originalData)
        # 分成 control 與 treatment 資料集
        get_split_all = splitData(merge_data)
        control_data, treatment_data = get_split_all.ct_split()
        # 分別將 control 與 treatment 再分割成 bb, bs, sb, ss...
        get_split_C = splitData(control_data)
        bb_C, bb_same_C, bb_diff_C, bs_C, sb_C, ss_C = get_split_C.sb_split()
        get_split_T = splitData(treatment_data)
        bb_T, bb_same_T, bb_diff_T, bs_T, sb_T, ss_T = get_split_T.sb_split()
    except:
        st.error('上傳的資料格式可能有誤！檢查是否已經清空後面空白欄位！')

else:
    pass

st.markdown('---')

st.header('資料分布情形')
st.markdown('- 檢視控制組/實驗組與沒門檻/有門檻的大小隊之分配情形')
# 建立資料表
try: 
    sb_distribution = [{'沒門檻/有門檻': '全部', 'Control': len(control_data), 'Treatment': len(treatment_data), '總計': len(merge_data)},
                    {'沒門檻/有門檻': '大大', 'Control': len(bb_C), 'Treatment': len(bb_T), '總計': len(bb_C) + len(bb_T)},
                    {'沒門檻/有門檻': '大大 (立場同)', 'Control': len(bb_same_C), 'Treatment': len(bb_same_T), '總計': len(bb_same_T) + len(bb_same_C)},
                    {'沒門檻/有門檻': '大大 (立場異)', 'Control': len(bb_diff_C), 'Treatment': len(bb_diff_T), '總計': len(bb_diff_T) + len(bb_diff_C)},
                    {'沒門檻/有門檻': '大小', 'Control': len(bs_C), 'Treatment': len(bs_T), '總計': len(bs_C) + len(bs_T)},
                    {'沒門檻/有門檻': '小大', 'Control': len(sb_C), 'Treatment': len(sb_T), '總計': len(sb_C) + len(sb_T)},
                    {'沒門檻/有門檻': '小小', 'Control': len(ss_C), 'Treatment': len(ss_T), '總計': len(ss_C) + len(ss_T)}]

    sb_distribution = pd.DataFrame(sb_distribution)
    st.write(sb_distribution.to_html(escape = False), unsafe_allow_html = True)
except:
    pass

st.markdown('---')

st.header('【C】有門檻 wtp v.s. 沒門檻 wtp')
st.markdown('- 僅使用 control 的資料表')
st.markdown('- 使用成對 t 檢定，檢視在不同隊伍分配情形下，有門檻 wtp 與沒門檻 wtp 是否有差別。')

try:
    if(len(control_data) != 0):
        
        groupList = ['全部', '大大', '大大 (立場同)', '大大 (立場異)', '大小', '小大', '小小']
        dataList = [control_data, bb_C, bb_same_C, bb_diff_C, bs_C, sb_C, ss_C]
        itemList = ['player.wtp_voting_cost', 'player.wtp_voting_cost_pq']        
        colList = ['沒門檻 wtp', '有門檻 wtp']

        all_group_result = pd.DataFrame()

        for group, data in zip(groupList, dataList):
            t_result = ttest(group = group, data1 = data, data2=data)
            wtp_mean = get_mean(group = group, data = data, item = 'player.wtp_voting_cost', colname = '沒門檻 wtp 平均')
            wtp_pq_mean = get_mean(group = group, data = data, item = 'player.wtp_voting_cost_pq', colname = '有門檻 wtp 平均')
            single_group = pd.merge(wtp_mean, wtp_pq_mean, on = ['沒門檻/有門檻'])
            single_group = pd.merge(single_group, t_result)
            all_group_result = pd.concat([all_group_result, single_group])
        
        all_group_result = pd.DataFrame(all_group_result).reset_index(drop = True)
        all_group_result['wtp 平均比較'] = all_group_result.apply(lambda x : x['沒門檻 wtp 平均'] > x['有門檻 wtp 平均'], axis = 1)
        all_group_result.loc[(all_group_result['wtp 平均比較'] == 1), 'wtp 平均比較'] = '沒門檻 > 有門檻'
        all_group_result.loc[(all_group_result['wtp 平均比較'] == 0), 'wtp 平均比較'] = '有門檻 > 沒門檻' 

        all_group_result = all_group_result.drop(['t-statistic'], axis = 1)
        all_group_result = all_group_result[['沒門檻/有門檻', '沒門檻 wtp 平均', '有門檻 wtp 平均', 'wtp 平均比較', 'p-value']]

        st.write(all_group_result.to_html(escape = False), unsafe_allow_html = True)    

        st.write('\n')

        show_detail = st.checkbox('檢視詳細 t 檢定資料')
        if (show_detail):
            for group, data in zip(groupList, dataList):
                st.write('\n')
                st.markdown(group)
                t_result = ttest(group = group, data1 = data, data2=data, completed = True)
                st.write(t_result.to_html(escape = False), unsafe_allow_html = True)
    else:
        st.markdown('```沒有控制組資料!```')
except:
    pass

st.markdown('---')

st.header('【C】大大 (同) 與大大 (異) 之非成對 t 檢定')
st.markdown('- 僅使用 control 資料表')
st.markdown('- 分別檢視在有門檻與沒門檻的情況')
try:
    if(len(control_data)!=0):
        pq = ttest(group, data1 = bb_same_C, data2 = bb_diff_C, item1 = 'player.wtp_voting_cost_pq', item2 = 'player.wtp_voting_cost_pq', completed = True, paired = False)
        no_pq = ttest(group, data1 = bb_same_C, data2 = bb_diff_C, item1 = 'player.wtp_voting_cost', item2 = 'player.wtp_voting_cost', completed = True, paired = False)
        st.markdown('有門檻')
        st.write(pq.to_html(escape = False), unsafe_allow_html = True)
        st.write('\n\n')
        st.markdown('沒門檻')
        st.write(no_pq.to_html(escape = False), unsafe_allow_html = True)
    
    else:
        st.markdown('```沒有控制組資料!```')
except:
    pass

st.markdown('---')

st.header('【C】隊伍大小以及有無門檻之交互作用')
st.markdown('- 僅使用 control 資料表')
st.markdown('- 另外也有提供沒有加入交叉項的模型')
st.markdown('- 模型設定:')
st.latex(r'wtp = \beta_0+\beta_1\times is\_large+\beta_2\times is\_pq+\beta_3\times is\_pq\times is\_large')
st.markdown('- 變數解釋: $wtp$ 為願付價格，$is\_large$ 則代表是否分配於大組，$is\_pq$ 則是該遊戲是否有門檻')

try:
    if(len(control_data) != 0):
        # select non_pq data
        non_pq_data = control_data[['player.id_in_group', 'player.wtp_voting_cost', 'player.is_large_team', 'session']]
        non_pq_data.loc[:,'is_pq'] = 0
        non_pq_data.columns = ['id','wtp', 'is_large', 'session', 'is_pq']

        # select pq data
        pq_data = control_data[['player.id_in_group','player.wtp_voting_cost_pq', 'player.is_large_team_pq', 'session']]
        pq_data.loc[:, 'is_pq'] = 1
        pq_data.columns = ['id','wtp', 'is_large', 'session', 'is_pq']

        # concat pq data and non_pq data
        wtp_data = pd.concat([non_pq_data, pq_data])

        # run linear regression for all
        int = linearRegression(formula = 'wtp ~ is_large + is_pq + is_large*is_pq', data = wtp_data)
        int_result = int.get_result()
        int_f = int.f_test(hypothesis = "is_pq + is_large:is_pq = 0")
        
        no_int = linearRegression(formula = 'wtp ~ is_large + is_pq ', data = wtp_data)
        no_int_result = no_int.get_result()

        st.subheader('有交乘項 - 全體')
        st.markdown('- 使用的資料是所有的觀測值')
        st.write(int_result.to_html(escape = False), unsafe_allow_html = True)
        st.write('\n\n')
        st.markdown('F test')
        st.write(int_f.to_html(escape = False), unsafe_allow_html = True)        

        st.markdown('---')

        # run regression for single player
        st.subheader('有交乘項 - 單一玩家')
        st.markdown('- 以一個玩家為單位建立模型，並紀錄 ```is_large``` 與 ```is_pq``` 之係數正負向結果')
        st.markdown('- 若有 $n$ 個玩家，則重複建立 $n$ 次模型')
        st.markdown('- 表中的數字代表變數係數符合情況之參加者人數')
        
        # 完整結果
        int_player = single_player_lm(wtp_data = wtp_data, interaction = True)
        int_completed_result = int_player.get_result()
        int_table = int_player.get_table()
        st.write(int_table.to_html(escape = False), unsafe_allow_html = True)

        st.markdown('---')

        st.subheader('沒交乘項 - 全體')
        st.write(no_int_result.to_html(escape = False), unsafe_allow_html = True)
        
        st.markdown('---')

        st.subheader('沒交乘項 - 單一玩家')
        no_int_player = single_player_lm(wtp_data = wtp_data, interaction = False)
        no_int_completed_result = no_int_player.get_result()
        no_int_table = int_player.get_table()
        st.write(no_int_table.to_html(escape = False), unsafe_allow_html = True)      

    else:
        st.markdown('```沒有控制組資料!```')

except:
    pass

st.markdown('---')

st.header('【C & T】控制組 wtp v.s. 實驗組 wtp')
st.markdown('- 使用 control 與 treatment 資料表')
st.markdown('- control 之 wtp 計算方式為兩個選舉 wtp 之和，treatment 的即為原本的 wtp')
st.markdown('- 使用非成對 t 檢定檢驗控制組 wtp 與實驗組 wtp 是否有差異')

try:
    if(len(treatment_data) == 0 or len(control_data) == 0):
        st.markdown('```要同時有控制組與實驗組資料```')

    # 取得資料集
    merge_data_dummy = add_dummy(merge_data)
    modify_wtp_data = modify_wtp(data = merge_data_dummy)

    modify_sum = modify_wtp_data.modify_all(mode = 'sum')
    modify_max = modify_wtp_data.modify_all(mode = 'max')
    modify_min = modify_wtp_data.modify_all(mode = 'min')
    modify_pq = modify_wtp_data.modify_all(mode = 'pq')
    modify_no_pq = modify_wtp_data.modify_all(mode = 'no_pq')

    split_sum = splitData(modify_sum)
    sum_C, sum_T = split_sum.ct_split()
    split_sum_C = splitData(sum_C)
    sum_bb_C, sum_bb_same_C, sum_bb_diff_C, sum_bs_C, sum_sb_C, sum_ss_C = split_sum_C.sb_split()
    split_sum_T = splitData(sum_T)
    sum_bb_T, sum_bb_same_T, sum_bb_diff_T, sum_bs_T, sum_sb_T, sum_ss_T = split_sum_T.sb_split()

    groupList = ['全部', '大大', '大大 (立場同)', '大大 (立場異)', '大小', '小大', '小小']
    dataList_C = [sum_C, sum_bb_C, sum_bb_same_C, sum_bb_diff_C, sum_bs_C, sum_sb_C, sum_ss_C]
    dataList_T = [sum_T, sum_bb_T, sum_bb_same_T, sum_bb_diff_T, sum_bs_T, sum_sb_T, sum_ss_T]
    itemList = ['wtp', 'wtp']        
    colList = ['控制組 wtp 平均', '實驗組 wtp 平均']

    ct_group_result = pd.DataFrame()

    for group, data_C, data_T in zip(groupList, dataList_C, dataList_T):
        t_result = ttest(group = group, data1 = data_C, data2=data_T, item1 = 'wtp', item2 ='wtp', paired=False)
        mean_C = get_mean(group = group, data = data_C, item = 'wtp', colname = '控制組 wtp 平均')
        mean_T = get_mean(group = group, data = data_T, item = 'wtp', colname = '實驗組 wtp 平均')
        single_group = pd.merge(mean_C, mean_T, on = ['沒門檻/有門檻'])
        single_group = pd.merge(single_group, t_result)
        ct_group_result = pd.concat([ct_group_result, single_group])

    ct_group_result = pd.DataFrame(ct_group_result).reset_index(drop = True)
    ct_group_result['wtp 平均比較'] = ct_group_result.apply(lambda x : x['控制組 wtp 平均'] > x['實驗組 wtp 平均'], axis = 1)
    ct_group_result.loc[(ct_group_result['wtp 平均比較'] == 1), 'wtp 平均比較'] = '控制組 > 實驗組'
    ct_group_result.loc[(ct_group_result['wtp 平均比較'] == 0), 'wtp 平均比較'] = '實驗組 > 控制組' 

    ct_group_result = ct_group_result.drop(['t-statistic'], axis = 1)
    ct_group_result = ct_group_result[['沒門檻/有門檻', '控制組 wtp 平均', '實驗組 wtp 平均', 'wtp 平均比較', 'p-value']]

    st.write(ct_group_result.to_html(escape = False), unsafe_allow_html = True)    

    st.write('\n')

    show_detail_1 = st.checkbox('檢視詳細 t 檢定資料',key=111)

    if(show_detail_1):
        for group, data_C, data_T in zip(groupList, dataList_C, dataList_T):
            st.write('\n')
            st.markdown(group)
            t_result = ttest(group = group, data1 = data_C, data2=data_T, item1 = 'wtp', item2 ='wtp', paired=False, completed=True)
            st.write(t_result.to_html(escape=False), unsafe_allow_html = True)

except:
    pass


st.markdown('---')

st.header('【C & T】是否有實驗組與隊伍大小之交互作用')
st.markdown('- 檢驗是否有 treatment effect 還有其與隊伍大小是否有交互作用')
st.markdown('- treatment 的 wtp 為原始數據, control 的 wtp 計算方法分為五種: 兩選舉之和、兩選舉中最大值、最小值、取有門檻、沒門檻')
st.markdown('- 模型設定:')
st.latex(r'wtp = \beta_0+\beta_1\times treatment+\beta_2\times sb+\beta_3\times bs +\beta_4\times bb +\beta_5\times sb\_treatment+\beta_6\times bs\_treatment+\beta_7\times bb\_treatment')
st.markdown('- 變數解釋: $wtp$ 為願付價格，$is\_large$ 則代表是否分配於大組，$is\_pq$ 則是該遊戲是否有門檻')


try:
    if (len(control_data) == 0 or len(treatment_data) == 0):
        st.markdown('```要同時有控制組與實驗組資料```')
    
    else: 
        hypothesisList = ['treatment + sb:treatment = 0', 'treatment + bs:treatment = 0', 'treatment + bb:treatment = 0']
        
        st.subheader('控制組當中的 wtp 為兩選舉 wtp 之和')
        st.markdown('control 的 wtp = $a + b$')

        model_sum = linearRegression(formula = 'wtp ~ treatment + sb + bs + bb + sb*treatment + bs*treatment + bb*treatment', data = modify_sum)
        summary_sum = model_sum.get_result(completed=False)
        st.write(summary_sum.to_html(escape = False), unsafe_allow_html = True)
        
        st.write('\n\n')
        st.markdown('F 檢定')
        f_sum = pd.DataFrame()

        for hypothesis in hypothesisList:
            f_sum = pd.concat([f_sum, model_sum.f_test(hypothesis = hypothesis)])
        
        f_sum.reset_index(drop = True, inplace = True)
        st.write(f_sum.to_html(escape = False), unsafe_allow_html = True)

        st.markdown('---')

        st.subheader('控制組當中的 wtp 為兩選舉 wtp 中最大值')
        st.markdown('control 的 wtp = $max(a, b)$')
        model_max = linearRegression(formula = 'wtp ~ treatment + sb + bs + bb + sb*treatment + bs*treatment + bb*treatment', data = modify_max)
        summary_max = model_max.get_result(completed=False)
        st.write(summary_max.to_html(escape = False), unsafe_allow_html = True)
       
        st.write('\n\n')
        st.markdown('F 檢定')       
        f_max = pd.DataFrame()

        for hypothesis in hypothesisList:
            f_max = pd.concat([f_max, model_max.f_test(hypothesis = hypothesis)])
        
        f_max.reset_index(drop = True, inplace = True)
        st.write(f_max.to_html(escape = False), unsafe_allow_html = True)

        st.markdown('---')

        st.subheader('控制組當中的 wtp 為兩選舉 wtp 中最小值')
        st.markdown('control 的 wtp = $min(a, b)$')
        model_min = linearRegression(formula = 'wtp ~ treatment + sb + bs + bb + sb*treatment + bs*treatment + bb*treatment', data = modify_min)
        summary_min = model_min.get_result(completed=False)
        st.write(summary_min.to_html(escape = False), unsafe_allow_html = True)

        f_min = pd.DataFrame()
        st.write('\n\n')
        st.markdown('F 檢定')

        for hypothesis in hypothesisList:
            f_min = pd.concat([f_min, model_min.f_test(hypothesis = hypothesis)])
        
        f_min.reset_index(drop = True, inplace = True)
        st.write(f_min.to_html(escape = False), unsafe_allow_html = True)

        st.markdown('---')

        st.subheader('控制組當中的 wtp 為有門檻遊戲的 wtp ')
        st.markdown('control 的 wtp = wtp_pq')
        model_pq = linearRegression(formula = 'wtp ~ treatment + sb + bs + bb + sb*treatment + bs*treatment + bb*treatment', data = modify_pq)
        summary_pq = model_pq.get_result(completed=False)
        st.write(summary_pq.to_html(escape = False), unsafe_allow_html = True)

        f_pq = pd.DataFrame()
        st.write('\n\n')
        st.markdown('F 檢定')

        for hypothesis in hypothesisList:
            f_pq = pd.concat([f_pq, model_pq.f_test(hypothesis = hypothesis)])
        
        f_pq.reset_index(drop = True, inplace = True)
        st.write(f_pq.to_html(escape = False), unsafe_allow_html = True)

        st.markdown('---')

        st.subheader('控制組當中的 wtp 為沒門檻遊戲的 wtp ')
        st.markdown('control 的 wtp = wtp_no_pq')
        model_no_pq = linearRegression(formula = 'wtp ~ treatment + sb + bs + bb + sb*treatment + bs*treatment + bb*treatment', data = modify_no_pq)
        summary_no_pq = model_no_pq.get_result(completed=False)
        st.write(summary_no_pq.to_html(escape = False), unsafe_allow_html = True)

        f_no_pq = pd.DataFrame()
        st.write('\n\n')
        st.markdown('F 檢定')

        for hypothesis in hypothesisList:
            f_no_pq = pd.concat([f_no_pq, model_no_pq.f_test(hypothesis = hypothesis)])
        
        f_no_pq.reset_index(drop = True, inplace = True)
        st.write(f_no_pq.to_html(escape = False), unsafe_allow_html = True)

except:
    pass


st.markdown('---')

st.header('資料下載點')
try:
    # merged data
    merge_all = download_link(merge_data, "merge_all.csv", "merge_all")
    merge_control = download_link(control_data, "merge_control.csv","merge_control" )
    merge_treatment = download_link(treatment_data, "merge_treatment.csv","merge_treatment" )
    st.markdown("合併資料:  " + merge_all + "  " + merge_control + "  " + merge_treatment, unsafe_allow_html=True)

    # wtp_data
    wtp_sum = download_link(modify_sum, "wtp_sum.csv", "wtp_sum")
    wtp_max = download_link(modify_max, "wtp_max.csv", "wtp_max")
    wtp_min = download_link(modify_min, "wtp_min.csv", "wtp_min")
    st.markdown("以三種模式處理控制組的 wtp 資料 :  " + wtp_sum + "  " + wtp_max + "  " + wtp_min, unsafe_allow_html=True)

    # single player regression
    int_single = download_link(int_completed_result, "single_interaction.csv", 'single_interaction')
    no_int_single = download_link(no_int_completed_result, "single_no_interaction.csv", 'single_no_interaction')
    st.markdown("單一玩家模型係數結果: " + int_single + " " + no_int_single, unsafe_allow_html=True)

except:
    pass

st.markdown('---')
st.header('下載分析報告')
st.markdown('- 要同時有控制組和實驗組資料才有報告!')
st.markdown('- 格式要再自己手動調整喔!')

try:
    all_group_result = round(all_group_result, 3)
    int_result = round(int_result, 3)
    int_f = round(int_f, 3)
    no_int_result = round(no_int_result, 3)
    int_table = round(int_table, 3)
    no_int_table = round(no_int_table, 3)
    ct_group_result = round(ct_group_result, 3)
    summary_sum = round(summary_sum, 3)
    summary_max = round(summary_max, 3)
    summary_min = round(summary_min, 3)
    summary_pq = round(summary_pq, 3)
    summary_no_pq = round(summary_no_pq, 3)
    f_sum = round(f_sum, 3)
    f_max = round(f_max, 3)
    f_min = round(f_min, 3)
    f_pq = round(f_pq, 3)
    f_no_pq = round(f_no_pq, 3)
    pq = round(pq, 3)
    no_pq = round(no_pq, 3)

    report = reportGenerator()
    report.basic_info(files = files, control_amount = len(control_data), treatment_amount=len(treatment_data))
    report.participants_distribution(distribution_table = sb_distribution)
    report.data_analysis(pq = pq, no_pq = no_pq, paired_table= all_group_result , largePq_int_all = int_result, largePq_int_f = int_f, largePq_int_sin = int_table, 
                        largePq_no_all = no_int_result, largePq_no_sin = no_int_table,
                        ct_wtp = ct_group_result, sum_reg = summary_sum, 
                        sum_f = f_sum, max_reg = summary_max, max_f = f_max, min_reg = summary_min, 
                        min_f = f_min, pq_reg = summary_pq, pq_f = f_pq, no_pq_reg = summary_no_pq, no_pq_f = f_no_pq)
    file = report.save_document()
    st.markdown(get_binary_file_downloader_html(file, file_label='Report'), unsafe_allow_html=True)
except:
    pass
