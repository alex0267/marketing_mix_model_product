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

def compareTables(df1,df2,quant,round=False):
    if round:
        total_df = pd.concat([df1.round(),df2.round()], axis =1)
    else:
        total_df = pd.concat([df1,df2], axis =1)
    print(total_df)

    total_df = total_df.loc[~(total_df==0).all(axis=1)]
    total_df['DIFF'] = total_df.iloc[:,0] - total_df.iloc[:,1]
    total_df['AVG'] = (total_df.iloc[:,0]+total_df.iloc[:,1])/2 
    total_df['REL_DIFF'] =total_df['DIFF']/total_df['AVG']

    # print(f"quantile 0.8 : {total_df['REL_DIFF'].quantile(q=0.8)}")
    # print(f"quantile 0.9 : {total_df['REL_DIFF'].quantile(q=0.9)}")
    # print(f"quantile 0.95 : {total_df['REL_DIFF'].quantile(q=0.95)}")

    difference = total_df['REL_DIFF'].quantile(q=quant)


    return difference,total_df

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
        


def comparePrediction(directory_1, directory_2, quant, maxDiff, round):

    df_1 = createFrame(directory_1, 'prediction')
    df_2 = createFrame(directory_2, 'prediction')

    difference , total_df= compareTables(df_1,df_2,quant=quant,round=round)  

    print('prediction comparison')
    print(total_df.describe)  
     

    #check if 95% quantile has below 10% of difference
    if (difference > maxDiff):
        print('Predictions DO NOT seem to be similar')
    else:
        print('¨Predictions seem to converge.')

    print(f'Difference at quantile: {difference}') 

def comparePredictionMeans(directory_1, directory_2,maxDiff,scope):
    df_1 = createFrame(directory_1, scope)
    df_2 = createFrame(directory_2, scope)

    difference ,total_df= compareTables(df_1,df_2,quant=0.9,round=False)

    print('mean comparison')
    print(scope)
    print(total_df.describe())  
    print(total_df['REL_DIFF'].quantile(0.95))
    print(total_df['REL_DIFF'].quantile(0.9))

    total_df.to_excel('total_df_means.xlsx')
    # if (total_df['REL_DIFF'] > maxDiff):
    #     print('Predictions DO NOT seem to be similar')
    # else:
    #     print('¨Predictions seem to converge.')

    # print(f'Difference at quantile: {difference}') 


def comparePredictionMeans2(directory_1, directory_2,maxDiff,scope):
    df_1 = pd.read_csv(f'{directory_1}/{scope}.csv')
    df_2 = pd.read_csv(f'{directory_2}/{scope}.csv')

    total_df = df_1.merge(df_2, on ='index')
    total_df['DIFF'] = total_df.iloc[:,1] - total_df.iloc[:,2]
    total_df['AVG'] = (total_df.iloc[:,1]+total_df.iloc[:,2])/2 
    total_df['REL_DIFF'] =total_df['DIFF']/total_df['AVG']

    if (total_df['REL_DIFF'].describe()['max'] > maxDiff):
        print(f'Test unsuccessful for {scope}- {total_df["REL_DIFF"].describe()["max"]} is above allowed threhold {maxDiff}')
        print(total_df['REL_DIFF'].describe())
    else:
        print(f'test successful for {scope}')



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

    #comparePrediction(directory_1, directory_2, quant=0.95, maxDiff = 0.1, round=False)
    comparePredictionMeans2(directory_1, directory_2,maxDiff = 0.05, scope = 'prediction_meansPerPredictionCollect')
    comparePredictionMeans2(directory_1, directory_2,maxDiff = 0.001, scope = 'prediction_meanOfTotalPredictionCollect')
    compareSpendings(directory_1, directory_2, round=False)

                      
    return 0