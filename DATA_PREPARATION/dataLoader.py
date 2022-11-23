import pandas as pd
import sys
import numpy as np
import sys

def filterByWeeks(uniqueWeeks, configurations):
    '''
    Filter dataframe by Weeks to fit the scope of the model defined in the configurations
    '''
    uniqueWeeks_df = uniqueWeeks[(uniqueWeeks['YEAR_WEEK'] == configurations['DATA_START']).idxmax():].reset_index()
    uniqueWeeks_df = uniqueWeeks_df[:(uniqueWeeks_df['YEAR_WEEK'] == configurations['DATA_END']).idxmax()+1] #+1 for inclusive

    uniqueWeeks_df = uniqueWeeks_df[(uniqueWeeks_df['YEAR_WEEK'] == configurations['DATA_START']).idxmax():].reset_index()
    uniqueWeeks_df = uniqueWeeks_df[:(uniqueWeeks_df['YEAR_WEEK'] == configurations['DATA_END']).idxmax()+1] #+1 for inclusive


    return uniqueWeeks_df

def treatCheckDf(check_df, truth_df):

    truth_df_brands = truth_df['BRAND'].unique()

    check_df = check_df.sort_values(by=['BRAND','YEAR_WEEK'])
    #some tables might have more brands than we want to predict on
    check_df= check_df[check_df['BRAND'].isin(truth_df_brands)]
    check_df = check_df[['BRAND','YEAR_WEEK']]
    #some tables might have multiple values for a brand, year combination
    check_df = check_df.drop_duplicates().reset_index(drop=True)

    return check_df


def treatTruthDf(truth_df):
    truth_df = truth_df.sort_values(by=['BRAND','YEAR_WEEK'])
    truth_df = truth_df[['BRAND','YEAR_WEEK']].reset_index(drop=True)

    return truth_df


def checkTable(truth_df, check_df):
    '''
    Compare the tables to make sure all brands and weeks are included
    '''

    truth_df = treatTruthDf(truth_df)
    check_df = treatCheckDf(check_df, truth_df)
    try:
        assert truth_df.equals(check_df)
    except:
        print('Dataframes are different')
        merge_df = truth_df.merge(check_df, on=['BRAND','YEAR_WEEK'],how='outer',indicator = True)
        merge_df = merge_df[merge_df['_merge']!='both'].reset_index()
        print(merge_df)
        sys.exit()



    return 0

def loadData(configurations):
    '''
    Load the dataframes that make up all parts of the model.
    Might include basic data cleaning tasks to change dataframes
    Performs basic checks to assess the completness of the data
    '''

    #brand specific volume sell out data
    #is chosen to be the truth table (for checks of brand and week completness of other tables)
    sellOut_df = pd.read_excel('DATA/CALENDAR_YEAR/FRA_SELL_OUT_COMPANY_MAPPING.xlsx')

    #not all tables have data in 2022 -> filter until last week of 2021 (202152)
    sellOut_df['YEAR'] = sellOut_df['YEAR_WEEK'].astype(str).str[:4]
    sellOut_df = sellOut_df[sellOut_df['YEAR'].isin(['2019','2020','2021'])]
    
    #touchpoint spendings data
    mediaExec_df = pd.read_excel('DATA/CALENDAR_YEAR/FRA_SPEND_MEDIA_EXECUTION_MAPPING.xlsx')
    #mediaExec has trailing zeros in year week - remove via int declaration
    mediaExec_df['YEAR_WEEK'] = mediaExec_df['YEAR_WEEK'].astype(np.int64)
    mediaExec_df['BRAND'] = mediaExec_df['BRAND'].replace(to_replace='mumm_champagne', value='precious_liquid')
    mediaExec_df['YEAR'] = mediaExec_df['YEAR_WEEK'].astype(str).str[:4]
    mediaExec_df = mediaExec_df[mediaExec_df['YEAR'].isin(['2019','2020','2021'])]

    checkTable(sellOut_df.copy(), mediaExec_df.copy())

    #distribution proxies
    sellOutDistribution_df = pd.read_excel('DATA/CALENDAR_YEAR/FRA_SELL_OUT_DISTRIBUTION_MAPPING.xlsx')
    sellOutDistribution_df['BRAND'] = sellOutDistribution_df['BRAND'].replace(to_replace='mumm_champagne', value='precious_liquid')
    sellOutDistribution_df['YEAR'] = sellOutDistribution_df['YEAR_WEEK'].astype(str).str[:4]
    sellOutDistribution_df = sellOutDistribution_df[sellOutDistribution_df['YEAR'].isin(['2019','2020','2021'])]
    checkTable(sellOut_df.copy(), sellOutDistribution_df.copy())

    #competition mapping
    sellOutCompetition_df = pd.read_excel('DATA/CALENDAR_YEAR/FRA_SELL_OUT_COMPETITORS_MAPPING.xlsx')

    #covid proxy
    covid_df = pd.read_excel('DATA/CALENDAR_YEAR/FRA_COVID_MEASURES.xlsx')

    #net sales for uplift and ROI calculation
    netSales_df = pd.read_excel('DATA/CALENDAR_YEAR/FRA_SELL_IN_MAPPING.xlsx')

    #list of unique weeks that are subject to event & seasonality engineering
    uniqueWeeks_df = pd.DataFrame(mediaExec_df['YEAR_WEEK'].unique())
    uniqueWeeks_df = uniqueWeeks_df.rename(columns={0:'YEAR_WEEK'})

    filteredUniqueWeeks_df = filterByWeeks(uniqueWeeks_df, configurations)


    
    return mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df, filteredUniqueWeeks_df,netSales_df
