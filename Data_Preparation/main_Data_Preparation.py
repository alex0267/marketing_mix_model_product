'''
Current status of development - V01:

DONE
- Merge dataframe pieces, clean rows

TO BE DONE
- Inclusion of normalization
- Check whether all brands are there for all weeks

'''

import seasonality
import promotion
#import testing
import pandas as pd
import numpy as np
import os

#get current working directory
#print(os.getcwd())

#import data - we define a list of unique weeks that are subject to event & seasonality engineering
media_exec_df = pd.read_csv('../data/FRA_SPEND_MEDIA_EXECUTION_MAPPING.csv')
unique_weeks = pd.DataFrame(media_exec_df['YEAR_WEEK'].unique())
unique_weeks = unique_weeks.rename(columns={0:'YEAR_WEEK'})

sell_out_df = pd.read_csv('../data/FRA_SELL_OUT_COMPANY_MAPPING.csv')
sell_out_competition_df = pd.read_csv('../data/FRA_SELL_OUT_COMPETITORS_MAPPING.csv')


def run():

    #define basic feature table
    feature_df = sell_out_df[["YEAR_WEEK","BRAND"]]

    #clean out empty brand rows
    feature_df.dropna(subset=["BRAND"], inplace=True)

    #add media execution variables AND merge
    media_exec = media_exec_df[["YEAR_WEEK", "BRAND", "TOUCHPOINT", "SPEND"]]
    feature_df = feature_df.merge(media_exec, on=["YEAR_WEEK","BRAND"])
        #turn media variables into columns with primary key ['YEAR_WEEK','BRAND','TOUCHPOINT'] by SPEND
    feature_df = feature_df.set_index(['YEAR_WEEK','BRAND','TOUCHPOINT'])['SPEND'].unstack().add_suffix('_SPEND').reset_index()

    #calculate event & seasonality features AND merge
    seasonality_df = seasonality.construct_seasonality_and_event_features(unique_weeks)
    feature_df = feature_df.merge(seasonality_df, on="YEAR_WEEK")

    #calculate promotion feature with 0.9 percentile reference level AND merge
    promotion_df = promotion.compute_price_discount_feature(sell_out_df, quantile_reference=0.9)
    promotion_df = promotion_df.rename(columns={"VOLUME_SO": "TARGET_VOL_SO", "relative_gap_to_90th_price": "PROMOTION_FEATURE"})
    feature_df = feature_df.merge(promotion_df, on=["YEAR_WEEK","BRAND"])

    #calculate competiton feature based on category
    #comp = testing.construct_price_competitors_feature(sell_out_competition_df)

    #normalize data

    # final output dataframe
    # feature_df.to_csv("feature_df.csv")
    feature_df.to_csv("feature_df.csv")

    return feature_df

run()