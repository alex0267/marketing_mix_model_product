
from tkinter import S
import DATA_PREPARATION.seasonality
import DATA_PREPARATION.promotion
import DATA_PREPARATION.distribution
import DATA_PREPARATION.price
import DATA_PREPARATION.epros
import HELPER_FUNCTIONS.normalization
import PYTEST.extractEntryData
import pandas as pd
import numpy as np
import yaml

def normalizeControl(control_df, responseModelConfig):
    
    for controlVar in responseModelConfig['NORMALIZATION_STEPS_CONTROL']:
        control_df[controlVar], scale = HELPER_FUNCTIONS.normalization.normalize_feature(control_df[controlVar],control_df[controlVar], [responseModelConfig['NORMALIZATION_STEPS_CONTROL'][controlVar]])


    return control_df

def filterByBrands(df, configurations):
    '''
    Filter dataframe by brands and sort in order brand, year_week to
    fit the scope of the model and define a single source of truth for the order of brand & year_week
    '''

    df = df[df['BRAND'].isin(configurations['BRANDS'])]
    df = df.sort_values(by=['BRAND', 'YEAR_WEEK'], ascending=True, inplace=False)
    df.reset_index(drop=True, inplace=True)

    return df

def filterByWeeks(feature_df, configurations, runBackTest, split):
    '''
    Filter dataframe by Weeks to fit the scope of the model defined in the configurations
    '''
    
    feature_df = feature_df[(feature_df['YEAR_WEEK'] == configurations['DATA_START']).idxmax():].reset_index()
    feature_df = feature_df[:(feature_df['YEAR_WEEK'] == configurations['DATA_END']).idxmax()+1] #+1 for inclusive
    
    if (runBackTest == True):
        feature_df = feature_df[(feature_df['YEAR_WEEK'].isin(split))].reset_index()
        feature_df.to_excel('feat.xlsx')
    print(feature_df)


    return feature_df

def normalizeFeatureDf(configurations, feature_df):

    #normalization via saturation parameters according to configurations
    feature_df[configurations['TOUCHPOINTS']], touchpoint_norms = HELPER_FUNCTIONS.normalization.normalize_feature(feature_df[configurations['TOUCHPOINTS']],feature_df[configurations['TOUCHPOINTS']], configurations['NORMALIZATION_STEPS_TOUCHPOINTS'])
    #normalization via max, logp1 according to configurations
    feature_df[configurations['TARGET']], target_df_norm = HELPER_FUNCTIONS.normalization.normalize_feature(feature_df[configurations['TARGET']],feature_df[configurations['TARGET']], configurations['NORMALIZATION_STEPS_TARGET'])

    return feature_df

def createFeatureDf(configurations, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df):
    '''
    Performs transformations on input data to create the feature_df
    '''
    
    #the media execution table is the basis of the feature_df
    feature_df = mediaExec_df[["YEAR_WEEK", "BRAND", "TOUCHPOINT", "SPEND"]]

    #turn touchpoint variables into columns (each touchpoint one column) with primary key ['YEAR_WEEK','BRAND','TOUCHPOINT'] by SPEND
    #this is how the data will be interpreted
    feature_df = feature_df.set_index(['YEAR_WEEK','BRAND','TOUCHPOINT'])['SPEND'].unstack().reset_index()

    feature_df = feature_df.merge(sellOut_df[["YEAR_WEEK","BRAND","VOLUME_SO"]], on=["YEAR_WEEK","BRAND"])
    feature_df = feature_df.rename(columns={'VOLUME_SO':'TARGET_VOL_SO'})

    seasonality_df = DATA_PREPARATION.seasonality.construct_seasonality_and_event_features(uniqueWeeks_df)
    feature_df = feature_df.merge(seasonality_df, on="YEAR_WEEK")

    promotion_df = DATA_PREPARATION.promotion.compute_price_discount_feature(sellOut_df.copy(),sellOutDistribution_df.copy(),configurations, quantile_reference=0.9)
    feature_df = feature_df.merge(promotion_df[["YEAR_WEEK","BRAND","promotion"]], on=["YEAR_WEEK","BRAND"])
    
    distribution_df = DATA_PREPARATION.distribution.construct_distribution_feature(sell_out_distribution_df = sellOutDistribution_df.copy(),
                                                                                  configurations = configurations,
                                                                                  quantile_reference_level=0)
    feature_df = feature_df.merge(distribution_df[["YEAR_WEEK","BRAND", "distribution"]], on=["YEAR_WEEK","BRAND"])

    epros_df = DATA_PREPARATION.epros.constructEprosFeature(sellOutDistribution_df.copy(), column = 'DISTRIBUTION_FEATURE')
    feature_df = feature_df.merge(epros_df[["YEAR_WEEK","BRAND","epros"]], on=["YEAR_WEEK","BRAND"])

    off_trade_visibility_df = DATA_PREPARATION.distribution.construct_off_trade_visibility_feature(sellOutDistribution_df.copy())
    feature_df = feature_df.merge(off_trade_visibility_df[["YEAR_WEEK","BRAND","off_trade_visibility"]], on=["YEAR_WEEK","BRAND"])

    price_df = DATA_PREPARATION.price.calculatePrice(sellOut_df.copy(), configurations)
    feature_df = feature_df.merge(price_df[["YEAR_WEEK","BRAND","AVERAGE_PRICE"]], on=["YEAR_WEEK","BRAND"])

    covid_df= covid_df[['YEAR_WEEK', 'OXFORD_INDEX']].rename(columns={'OXFORD_INDEX':'covid'})
    feature_df = feature_df.merge(covid_df[['YEAR_WEEK','covid']], on='YEAR_WEEK', how='left')
    #covid table does not start until beginning of 2020
    feature_df = feature_df.fillna(0)

    return feature_df

def run(configurations, responseModelConfig, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df, runBackTest,split):
    '''
    input:
    Company-specific dataframes

    Execute data preparation pipeline to:
     - create features according to the configurations
     - create the normalized features
     - filter the data according to the scope

     Output:
     - feature_df - for documentation
     - filtered_feature_df - for simulation and output generation
     - normalized_feature_df (might not be necessary)
     - normalized_filtered_feature_df - for training

    '''

    feature_df = createFeatureDf(configurations, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df)
    
    feature_df = filterByBrands(feature_df.copy(),configurations)

    normalizedFeature_df = normalizeFeatureDf(configurations, feature_df.copy())

    #normalized features require the total scope of weeks since the normalization 
    #is done with maximum values across the entire dataset
    filteredFeature_df = filterByWeeks(feature_df.copy(), configurations, runBackTest, split)
    normalizedFilteredFeature_df = filterByWeeks(normalizedFeature_df.copy(), configurations,runBackTest, split)

    #index dataframe to filter other frames based on brand or year specifications (necessary for output generation)
    index_df = filteredFeature_df[['YEAR_WEEK','BRAND']]
    index_df['YEAR'] = index_df['YEAR_WEEK'].astype(str).str[:4]

    index_df.to_excel('ind.xlsx')

    PYTEST.extractEntryData.extractEntryData(feature_df, 'feature_df', configurations['SET_MASTER'])
    PYTEST.extractEntryData.extractEntryData(normalizedFilteredFeature_df, 'normalizedFilteredFeature_df', configurations['SET_MASTER'])

    return feature_df, filteredFeature_df, normalizedFeature_df, normalizedFilteredFeature_df, index_df
