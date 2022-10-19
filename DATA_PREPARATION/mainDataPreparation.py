from tkinter import S
import DATA_PREPARATION.seasonality
import DATA_PREPARATION.promotion
import DATA_PREPARATION.distribution
import DATA_PREPARATION.calculatePrice
import DATA_PREPARATION.epros
import HELPER_FUNCTIONS.normalization
import pandas as pd
import numpy as np
import yaml

#get current working directory
#print(os.getcwd())



def normalizeControl(control_df, responseModelConfig):
    
    for controlVar in responseModelConfig['NORMALIZATION_STEPS_CONTROL']:
        control_df[controlVar], scale = HELPER_FUNCTIONS.normalization.normalize_feature(control_df[controlVar],control_df[controlVar], [responseModelConfig['NORMALIZATION_STEPS_CONTROL'][controlVar]])


    return control_df

def filterByScope(df, configurations):
    '''
    Filter dataframe by brands and sort in order brand, year_week to
    fit the scope of the model and define a single source of truth for the order of brand & year_week
    '''
    

    df = df[df['BRAND'].isin(configurations['BRANDS'])]
    df = df.sort_values(by=['BRAND', 'YEAR_WEEK'], ascending=True, inplace=False)
    df.reset_index(drop=True, inplace=True)

    return df

def normalizeFeatureDf(configurations, feature_df):


    return 0

def createFeatureDf(configurations, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks):
    
    #the media execution table is the basis of the feature_df
    feature_df = mediaExec_df[["YEAR_WEEK", "BRAND", "TOUCHPOINT", "SPEND"]]

    #turn touchpoint variables into columns (each touchpoint one column) with primary key ['YEAR_WEEK','BRAND','TOUCHPOINT'] by SPEND
    #this is how the data will be interpreted
    feature_df = feature_df.set_index(['YEAR_WEEK','BRAND','TOUCHPOINT'])['SPEND'].unstack().reset_index()

    feature_df = feature_df.merge(sellOut_df[["YEAR_WEEK","BRAND","VOLUME_SO"]], on=["YEAR_WEEK","BRAND"])
    feature_df = feature_df.rename(columns={'VOLUME_SO':'TARGET_VOL_SO'})

    seasonality_df = DATA_PREPARATION.seasonality.construct_seasonality_and_event_features(uniqueWeeks)
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

    price_df = DATA_PREPARATION.calculatePrice.calculatePrice(sellOut_df.copy(), configurations)
    feature_df = feature_df.merge(price_df[["YEAR_WEEK","BRAND","AVERAGE_PRICE"]], on=["YEAR_WEEK","BRAND"])

    covid_df= covid_df[['YEAR_WEEK', 'OXFORD_INDEX']].rename(columns={'OXFORD_INDEX':'covid'})
    feature_df = feature_df.merge(covid_df[['YEAR_WEEK','covid']], on='YEAR_WEEK', how='left')

    return feature_df, price_df, seasonality_df

def run(configurations, responseModelConfig, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks):
    '''
    input:
    Company-specific dataframes

    Execute data preparation pipeline to:
     - create features according to the configurations
     - create the normalized features
     - filter the data according to the scope

     Output:
     - feature_df
     - normalized_feature_df
     - normalized_filtered_feature_df

    '''

    feature_df, price_df,seasonality_df = createFeatureDf(configurations, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks)
    feature_df = feature_df.fillna(0)
    

    normalizedFeature_df = normalizeFeatureDf(configurations, feature_df)

    filteredFeature_df = filterByScope(feature_df,configurations)

    #define raw spendings dataframe
    spendings_df = filteredFeature_df[configurations['TOUCHPOINTS']]

    #define target
    targetRaw = filteredFeature_df[configurations['TARGET']]
    control_df = feature_df[['YEAR_WEEK','BRAND','distribution', 'promotion', 'epros', 'covid','off_trade_visibility']]
    control_df = control_df.fillna(0)
    control_df = filterByScope(control_df,configurations)
    
    #define index columns as a reference for year scoping and dataset length
    indexColumns = pd.DataFrame()
    indexColumns['YEAR_WEEK'] = filteredFeature_df['YEAR_WEEK']
    indexColumns['YEAR'] = filteredFeature_df['YEAR_WEEK'].astype(str).str[:4]



    return spendings_df, seasonality_df, price_df, feature_df, targetRaw, indexColumns, control_df