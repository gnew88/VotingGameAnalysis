import pandas as pd
import re
import os

"""轉換資料型態"""
class dataProcessing:
    def __init__(self, file):
        self.file = file
        self.data = pd.read_csv(file) 
        self.roundNum = 30
        self.playerNum = 15
        
    ######### Modify columns #########
    def modifyCol(self):
        
        # add the column to identify whether it is treatment or control 
        self.data['treatment'] = 0
        self.data.loc[(self.data['session.config.name'] == 'voting_treatment'), 'treatment'] = 1
        
        # remove control/treatment and number
        new_col = []
        
        pattern = "(voting|survey)_(control|treatment)\.[0-9]{1,2}\."
        for col in self.data.columns:
            new_col.append(re.sub(pattern, '', col))
        
        self.data.columns = new_col
        
    ######## Extract voting data ########
    def splitVoteData(self):
        # modify column name
        self.modifyCol()
        # the first and last item of a round
        firstItem = 'player.id_in_group'
        lastItem = 'subsession.round_row'
        
        # obtain their indices
        firstIdx = list(self.data.columns).index(firstItem)
        lastIdx = list(self.data.columns).index(lastItem)
        
        # the interval size of round1
        interval = lastIdx - firstIdx + 1
        
        # the ideal index of the lastItem of round30
        round30LastIdx = firstIdx + interval * self.roundNum - 1
        
        # whether the data has equal interval
        if (self.data.columns[round30LastIdx] == lastItem):
            # split the data into votingData and otherData(introduction, survey)
            votingData = self.data.iloc[:,firstIdx:round30LastIdx+1]
            otherData = pd.concat([self.data.iloc[:,:firstIdx], 
                                   self.data.iloc[:,round30LastIdx+1:]], 
                                   axis = 1)
            return votingData, otherData
            
        else:
            print('interval is not equal')
            return False
        
    ######## Extract the columns #########
    def extractCol(self, extractFile = r'extractCol.csv'):
        # get votingData and otherData
        try:
            votingData, otherData = self.splitVoteData()
        except: 
            print('Something wrong')
            return False
            
        # get the columns we need
        voteCol = pd.read_csv(extractFile)['vote'].to_list()
        voteCol = [col for col in voteCol if str(col) != 'nan']
        
        otherCol = pd.read_csv(extractFile)['survey'].to_list()
        otherCol = [col for col in otherCol if str(col) != 'nan']

        # select dataframe
        extractedVote = votingData.loc[:, votingData.columns.isin(voteCol)]
        extractedOther = otherData.loc[:, otherData.columns.isin(otherCol)]
        
        return extractedVote, extractedOther         
    
    ######## Reshape data ########
    def reshapeData(self):
        # new dataframe
        processedData = pd.DataFrame()
        
        # get extractedVote and extractedOther
        extractVote, extractOther = self.extractCol()
        
        # process extractVote
        interval = int(len(extractVote.columns) / self.roundNum)
        
        if (len(extractVote.columns) % self.roundNum == 0):
        
            for player in range(self.playerNum):
                for num in range(self.roundNum):
                    dataRow = pd.DataFrame(extractVote.iloc[player, num * interval:(num + 1) * interval]).T
                    processedData = pd.concat([processedData, dataRow])
                    processedData = processedData.reset_index(drop=True)
            
        else:
            print('Something wrong')
            return False
        
        # merge with extractOther
        finalData = pd.merge(left = processedData, 
                    right = extractOther, 
                    on = ['player.id_in_group'])
        
        
        # add column to identify the round number
        finalData['round_num'] = [*range(1,self.roundNum + 1)]*self.playerNum

        return finalData
    
    ####### Add column to identify sesseion
    def addSession(self):
        # get data
        data = self.reshapeData()
        # set the file name as session
        fileName = self.file.name.replace('.csv', '')
        data['session'] = fileName    
        return data
    
    # Identify the condition: small-big, big-small, big-big (1, 2), big-small
    def completedProcess(self):
        
        df = self.addSession()
        
        # bb, bs, ss, sb
        df.loc[((df['player.is_large_team'] == 1) & (df['player.is_large_team_pq'] == 1)), 'sb_condition'] = 'bb'
        df.loc[((df['player.is_large_team'] == 1) & (df['player.is_large_team_pq'] == 0)), 'sb_condition'] = 'bs'
        df.loc[((df['player.is_large_team'] == 0) & (df['player.is_large_team_pq'] == 1)), 'sb_condition'] = 'sb'
        df.loc[((df['player.is_large_team'] == 0) & (df['player.is_large_team_pq'] == 0)), 'sb_condition'] = 'ss'

       # bb has two cases: pq_same, pq_different (team member) 

        for num in range(1, self.roundNum + 1):

            obsNum = len(df.loc[((df['sb_condition'] == 'bb') & (df['round_num'] == num))])

            if (obsNum == 1):
                df.loc[((df['sb_condition'] == 'bb') & (df['round_num'] == num)), 'bb_pq'] = 'different'    
            if(obsNum == 8):
                df.loc[((df['sb_condition'] == 'bb') & (df['round_num'] == num)), 'bb_pq'] = 'same'    

        return df

"""合併資料"""
def mergingData(files):

    merge_data = pd.DataFrame()

    for file in files:
        processed = dataProcessing(file)
        reshape_data = processed.completedProcess()
        merge_data = pd.concat([merge_data, reshape_data])

    return merge_data