from lib2to3.pgen2.pgen import DFAState
import yaml
import sys
import numpy as np
import pandas as pd
# from tqdm import tqdm
from sklearn.model_selection import KFold

# sys.path.append('../MARKETING_MIX_MODEL_PRODUCT')
# sys.path.append('..')

from DATA_PREPARATION.dataLoader import loadData
import runPipeline

# import runPipeline


'''
Application of k-fold cross validation back test

goal:
Assure cobustness of the model my calculating the R2 only on a test sample

challenges:
- Covid period might need to be analysed seperately (start with back test from 2018- beginning of 2020 at first)

restrictions:
- k not multiple of years analysed (2018-2021 = 3)

'''

def split_df(df, index, splits):

    #print(uniqueChildren)
    df = pd.DataFrame()

    for i in index:
            df = pd.concat([df,splits[i]])


    return df['YEAR_WEEK']

def divideIndexInFolds(uniqueWeeks_df, nbrOfFolds):
        splits = np.array_split(uniqueWeeks_df, nbrOfFolds)

        return splits


def runBackTest():

        #Define configurations to be used
        with open('CONFIG/baseConfig.yaml', 'r') as file:
                configurations = yaml.safe_load(file)

        with open('CONFIG/testConfig.yaml', 'r') as file:
                testConfig = yaml.safe_load(file)

        

        mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df, filteredUniqueWeeks_df = loadData(configurations)

        #filteredUniqueWeeks is not split directly via KFold since otherwise splits are taken at random throughout the dataset
        #we require windows since we are dealing with a time series
        splits = divideIndexInFolds(filteredUniqueWeeks_df, testConfig['NUMBER_OF_FOLDS'])

        kf = KFold(n_splits=testConfig['NUMBER_OF_FOLDS'], shuffle=True, random_state=3)

        nrFold = 0
        results_dict={}

        for train_index, test_index in (kf.split(splits)):
                nrFold = nrFold +1
                

                train_split = split_df(filteredUniqueWeeks_df,train_index,splits)

                r2 = runPipeline.run(runBackTest = True, split = train_split, name = f'r2_Backtest_fold_NO_COVID_{nrFold}', load = False)
                print(f'TRAIN - r2_Backtest_fold_NO_COVID_{nrFold}: {r2}')
                results_dict[f'TRAIN - r2_Backtest_fold_NO_COVID_{nrFold}'] = r2
                
                test_split = split_df(filteredUniqueWeeks_df,test_index,splits)

                r2 = runPipeline.run(runBackTest = True, split = test_split, name = f'r2_Backtest_fold_NO_COVID_{nrFold}', load = True)
                print(f'TEST - r2_Backtest_fold_NO_COVID_{nrFold}: {r2}')
                results_dict[f'TEST - r2_Backtest_fold_NO_COVID_{nrFold}'] = r2

        print(results_dict)

 


        return 0    



runBackTest()