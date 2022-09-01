'''
Current status of development - V01:

DONE
- Merge dataframe pieces, clean rows

TO BE DONE
- Inclusion of normalization
- Check whether all brands are there for all weeks
'''

import Data_Preparation.seasonality
import Data_Preparation.promotion
#import testing
import pandas as pd
import numpy as np
import yaml

#get current working directory
#print(os.getcwd())

#import data - we define a list of unique weeks that are subject to event & seasonality engineering
media_exec_df = pd.read_csv('data/FRA_SPEND_MEDIA_EXECUTION_MAPPING.csv')
unique_weeks = pd.DataFrame(media_exec_df['YEAR_WEEK'].unique())
unique_weeks = unique_weeks.rename(columns={0:'YEAR_WEEK'})

sell_out_df = pd.read_csv('data/FRA_SELL_OUT_COMPANY_MAPPING.csv')
sell_out_competition_df = pd.read_csv('data/FRA_SELL_OUT_COMPETITORS_MAPPING.csv')


def run():

    #define basic feature table
    feature_df = sell_out_df[["YEAR_WEEK","BRAND"]]

    #clean out empty brand rows
    feature_df.dropna(subset=["BRAND"], inplace=True)

    #add media execution variables AND merge
    media_exec = media_exec_df[["YEAR_WEEK", "BRAND", "TOUCHPOINT", "SPEND"]]

    feature_df = feature_df.merge(media_exec, on=["YEAR_WEEK","BRAND"])
        #turn media variables into columns with primary key ['YEAR_WEEK','BRAND','TOUCHPOINT'] by SPEND
    feature_df = feature_df.set_index(['YEAR_WEEK','BRAND','TOUCHPOINT'])['SPEND'].unstack().reset_index()


    #calculate event & seasonality features AND merge
    seasonality_df = Data_Preparation.seasonality.construct_seasonality_and_event_features(unique_weeks)
    feature_df = feature_df.merge(seasonality_df, on="YEAR_WEEK")

    #calculate promotion feature with 0.9 percentile reference level AND merge
    promotion_df = Data_Preparation.promotion.compute_price_discount_feature(sell_out_df, quantile_reference=0.9)
    promotion_df = promotion_df.rename(columns={"VOLUME_SO": "TARGET_VOL_SO", "relative_gap_to_90th_price": "PROMOTION_FEATURE"})
    feature_df = feature_df.merge(promotion_df, on=["YEAR_WEEK","BRAND"])

    #calculate competiton feature based on category
    #comp = testing.construct_price_competitors_feature(sell_out_competition_df)

    #drop touchpoint fiona since it does not have definitions allocated
    feature_df = feature_df.drop('fiona', axis=1)

    #load config file (yaml)
    with open('config/baseConfig.yaml', 'r') as file:
        configurations = yaml.safe_load(file)

    #filter dataframe by brands in scope
    feature_df = feature_df[feature_df['BRAND'].isin(configurations['BRANDS'])]
    feature_df.reset_index(drop=True, inplace=True)

    #filter promotion_df to fit scope
    promotion_df = promotion_df[promotion_df['BRAND'].isin(configurations['BRANDS'])]
    promotion_df.reset_index(drop=True, inplace=True)
    promotion_df = promotion_df[configurations['CONTROL_VARIABLES_BASE']]


    #filter seasonality_df to fit scope
    seasonality_df = seasonality_df[configurations['SEASONALITY_VARIABLES_BASE']]

    #define raw spendings dataframe
    spendings_df = feature_df[configurations['TOUCHPOINTS']]
    
    #define target
    target_raw = feature_df[configurations['TARGET']]

    # final output dataframe
    feature_df.to_csv("feature_df.csv")
    
    
    return spendings_df, feature_df, seasonality_df, promotion_df, target_raw


