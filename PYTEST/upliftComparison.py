import pandas as pd
import numpy as np
import json
import os
import PYTEST.upliftComparison




def createFrame(directory,scope):
    df = pd.DataFrame()
    for file in os.listdir(directory):

        if(str(file)[:len(scope)] == scope):
            f = pd.read_csv(f'{directory}/{file}')
            df = pd.concat([df,f], axis=0)

    return df.iloc[:,1:].rename(columns={'0':str(directory)[33:]})



def compareSpendings(directory_1, directory_2, round):

    df_1 = createFrame(directory_1, 'spendings')
    df_2 = createFrame(directory_2, 'spendings')

    if (round):
        equal = df_1.round().equals(df_2.round())
    else:
        equal = df_1.equals(df_2)

    if (equal):
        print('Spendings are the same')
        
    else:
        print('Spendings DO NOT seem to be similar')
        


def comparePredictions(directory_1, directory_2,maxDiff,scope, test, quantile = None):
    df_1 = pd.read_csv(f'{directory_1}/{scope}.csv')
    df_2 = pd.read_csv(f'{directory_2}/{scope}.csv')

    total_df = df_1.merge(df_2, on ='index')
    total_df['DIFF'] = total_df.iloc[:,1] - total_df.iloc[:,2]
    total_df['AVG'] = (total_df.iloc[:,1]+total_df.iloc[:,2])/2 
    total_df['REL_DIFF'] = abs(total_df['DIFF']/total_df['AVG'])
    total_df = total_df.fillna(0)
    total_df = total_df[total_df['AVG'] != 0]

    if(test == 'maxDiff'):
        threshold = total_df['REL_DIFF'].describe()['max'] 
    elif (test =='quantileBased'):
        threshold = total_df['REL_DIFF'].quantile(q=quantile)

    if (threshold > maxDiff):
        print(f'Test unsuccessful for {scope} : {threshold} is above allowed threhold {maxDiff}')
        print(total_df['REL_DIFF'].describe())
        print(total_df['REL_DIFF'].quantile(q=0.95))
        print(total_df['REL_DIFF'].quantile(q=0.99))
        total_df.to_excel('total_df.xlsx')
    else:
        print(f'Test successful for {scope} : {threshold} is below allowed threhold {maxDiff}')


def compareUplifts():
    '''
    Comparing the calculated uplifts between the master and the test.
    Comparison is done for spendings and prediction of all touchpoint and subset combination.
    As uplifts the values 1.6 and 0.6 were chosen for comparison.
    The comparison is based on a quantile approach the relative difference between the two datasets.
    The predictions are calculated via the delta meaning prediction(x spending level)-prediction(0 spending level) to measure true impact.
    The approach contains the following parameters:

    -
    quant: The quantile the relative difference should be taken from
    maxDiff: The maximum allowed relative difference at that quantile
    round: If rounding of the dataset is allowed
    '''

    directory_1 = 'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_MASTER'
    directory_2 = 'PYTEST/COMPARE_FRAMES/UPLIFT_COMPARISON_TEST'

    comparePredictions(directory_1, directory_2,maxDiff = 0.05, scope = 'prediction_meansPerPredictionCollect', test='quantileBased', quantile = 0.95)
    comparePredictions(directory_1, directory_2,maxDiff = 0.001, scope = 'prediction_meanOfTotalPredictionCollect',test='maxDiff')
    comparePredictions(directory_1, directory_2,maxDiff = 0.1, scope = 'prediction_weeklyPredictionCollect',test='quantileBased', quantile = 0.95)
    compareSpendings(directory_1, directory_2, round=False)

                      
    return 0