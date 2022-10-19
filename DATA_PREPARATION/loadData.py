import pandas as pd
import sys

def checkTable(truth_df, check_df):
    '''
    Compare the tables to make sure all brands and weeks are included
    '''
    truth_df_brands = truth_df['BRAND'].unique()
    truth_df = truth_df.sort_values(by=['BRAND','YEAR_WEEK'])
    truth_df = truth_df[['BRAND','YEAR_WEEK']].reset_index(drop=True)

    check_df = check_df.sort_values(by=['BRAND','YEAR_WEEK'])
    #some tables might have more brands than we want to predict on
    check_df= check_df[check_df['BRAND'].isin(truth_df_brands)]
    check_df = check_df[['BRAND','YEAR_WEEK']]
    #some tables might have multiple values for a brand, year combination
    check_df = check_df.drop_duplicates().reset_index(drop=True)
    

    if (truth_df.equals(check_df) == False):
        print(f'DATAFRAMES ARE NOT THE SAME!')
        print(truth_df)
        print(check_df)
        exit()

    return 0

def loadData():
    '''
    Load the dataframes that make up all parts of the model.
    Might include basic data cleaning tasks to change dataframes
    Performs basic checks to assess the completness of the data
    '''

    #brand specific volume sell out data
    #is chosen to be the truth table (for checks of brand and week completness of other tables)
    sellOut_df = pd.read_csv('DATA/FRA_SELL_OUT_COMPANY_MAPPING_EDIT.csv')
    
    #touchpoint spendings data
    mediaExec_df = pd.read_csv('DATA/FRA_SPEND_MEDIA_EXECUTION_MAPPING.csv')
    mediaExec_df['BRAND'] = mediaExec_df['BRAND'].replace(to_replace='mumm_champagne', value='precious_liquid')
    checkTable(sellOut_df.copy(), mediaExec_df.copy())

    #distribution proxies
    sellOutDistribution_df = pd.read_csv('DATA/FRA_SELL_OUT_DISTRIBUTION_MAPPING.csv')
    sellOutDistribution_df['BRAND'] = sellOutDistribution_df['BRAND'].replace(to_replace='mumm_champagne', value='precious_liquid')
    checkTable(sellOut_df.copy(), sellOutDistribution_df.copy())

    #competition mapping
    sellOutCompetition_df = pd.read_csv('DATA/FRA_SELL_OUT_COMPETITORS_MAPPING.csv')

    #covid proxy
    covid_df = pd.read_csv('DATA/FRA_COVID_MEASURES.csv')

    #list of unique weeks that are subject to event & seasonality engineering
    uniqueWeeks = pd.DataFrame(mediaExec_df['YEAR_WEEK'].unique())
    uniqueWeeks = uniqueWeeks.rename(columns={0:'YEAR_WEEK'})


    
    return mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks
