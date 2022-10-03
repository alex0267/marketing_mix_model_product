from tkinter import S
import DATA_PREPARATION.seasonality
import DATA_PREPARATION.promotion
import DATA_PREPARATION.distribution
import DATA_PREPARATION.calculatePrice
import pandas as pd
import numpy as np
import yaml

#get current working directory
#print(os.getcwd())

#import data - we define a list of unique weeks that are subject to event & seasonality engineering
mediaExec_df = pd.read_csv('DATA/FRA_SPEND_MEDIA_EXECUTION_MAPPING.csv')
sellOut_df = pd.read_csv('DATA/FRA_SELL_OUT_COMPANY_MAPPING_EDIT.csv')
sellOutDistribution_df = pd.read_csv('DATA/FRA_SELL_OUT_DISTRIBUTION_MAPPING.csv')
sellOutCompetition_df = pd.read_csv('DATA/FRA_SELL_OUT_COMPETITORS_MAPPING.csv')
covid_df = pd.read_csv('DATA/FRA_COVID_MEASURES.csv')

    #clean data - replace mumm_champagne by precious_liquid
mediaExec_df['BRAND'] = mediaExec_df['BRAND'].replace(to_replace='mumm_champagne', value='precious_liquid')

uniqueWeeks = pd.DataFrame(mediaExec_df['YEAR_WEEK'].unique())
uniqueWeeks = uniqueWeeks.rename(columns={0:'YEAR_WEEK'})


#clean data - replace mumm_champagne by precious_liquid
sellOutDistribution_df['BRAND'] = sellOutDistribution_df['BRAND'].replace(to_replace='mumm_champagne', value='precious_liquid')



def filterByScope(df, configurations):
    '''
    Filter dataframe by brands and sort in order brand, year_week to
    fit the scope of the model and define a single source of truth for the order of brand & year_week
    '''
    

    df = df[df['BRAND'].isin(configurations['BRANDS'])]
    df = df.sort_values(by=['BRAND', 'YEAR_WEEK'], ascending=True, inplace=False)
    df.reset_index(drop=True, inplace=True)

    return df

def run(configurations):
    '''
    Execute data preparation pipeline to create features according to the configurations
    that the models will be trained with.
    '''

    #define basic feature table as all brand indices
    brandIndices = sellOut_df[["YEAR_WEEK","BRAND"]]

    #clean out empty brand rows
    #feature_df.dropna(subset=["BRAND"], inplace=True)

    #add media execution variables AND merge
    mediaExec = mediaExec_df[["YEAR_WEEK", "BRAND", "TOUCHPOINT", "SPEND"]]


    feature_df = brandIndices.merge(mediaExec, on=["YEAR_WEEK","BRAND"])
        #turn media variables into columns with primary key ['YEAR_WEEK','BRAND','TOUCHPOINT'] by SPEND
    feature_df = feature_df.set_index(['YEAR_WEEK','BRAND','TOUCHPOINT'])['SPEND'].unstack().reset_index()


    #calculate event & seasonality features AND merge
    seasonality_df = DATA_PREPARATION.seasonality.construct_seasonality_and_event_features(uniqueWeeks)
    feature_df = feature_df.merge(seasonality_df, on="YEAR_WEEK")

    #calculate promotion feature with 0.9 percentile reference level AND merge
    promotion_df = DATA_PREPARATION.promotion.compute_price_discount_feature(sellOut_df.copy(), quantile_reference=0.9)
    promotion_df = promotion_df.rename(columns={"VOLUME_SO": "TARGET_VOL_SO", "relative_gap_to_90th_price": "promotion"})
    feature_df = feature_df.merge(promotion_df, on=["YEAR_WEEK","BRAND"])
    control_df = brandIndices.merge(promotion_df[['YEAR_WEEK','BRAND', 'promotion']], how='inner', on=['YEAR_WEEK','BRAND'])

    #calculate competiton feature based on category
    #comp = testing.construct_price_competitors_feature(sell_out_competition_df)
    
    distribution_df = DATA_PREPARATION.distribution.construct_distribution_feature(sell_out_distribution_df = sellOutDistribution_df,
                                                                                  configurations = configurations,
                                                                                  quantile_reference_level=0)
    
    distribution_df = distribution_df[["YEAR_WEEK","BRAND", "distribution"]]

    feature_df = feature_df.merge(distribution_df, on=["YEAR_WEEK","BRAND"])
    
    #drop touchpoint fiona since it does not have definitions allocated
    #feature_df = feature_df.drop('fiona', axis=1)

    #control_df = brand_Indices.merge(promotion_df, how='inner', on=['YEAR_WEEK','BRAND'])
    control_df = control_df.merge(distribution_df, how='inner', on=['YEAR_WEEK','BRAND'])


    #create price_df
    price_df = DATA_PREPARATION.calculatePrice.calculatePrice(sellOut_df.copy(), configurations)
    feature_df = feature_df.merge(price_df, on=["YEAR_WEEK","BRAND"])


    covid_feature = covid_df[['YEAR_WEEK', 'OXFORD_INDEX']].rename(columns={'OXFORD_INDEX':'covid'})
    control_df = control_df.merge(covid_feature, on='YEAR_WEEK', how='left')
    control_df = control_df.fillna(0)
    print(control_df)
 

    filteredFeature_df = filterByScope(feature_df,configurations)


    #define raw spendings dataframe
    spendings_df = filteredFeature_df[configurations['TOUCHPOINTS']]

    #define target
    targetRaw = filteredFeature_df[configurations['TARGET']]

    #control df
    control_df = filterByScope(control_df,configurations)

    #price df
    price_df = filterByScope(price_df,configurations)
    
    
    #define index columns as a reference for year scoping and dataset length
    indexColumns = pd.DataFrame()
    indexColumns['YEAR_WEEK'] = filteredFeature_df['YEAR_WEEK']
    indexColumns['YEAR'] = filteredFeature_df['YEAR_WEEK'].astype(str).str[:4]

    #print(control_df)
    control_df.to_excel('OUTPUT_DF/control_df.xlsx')

    return spendings_df, seasonality_df, price_df, feature_df, control_df, targetRaw, indexColumns