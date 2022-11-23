
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

def filterByBrands(df, baseConfig):
    '''
    Filter dataframe by brands and sort in order brand, year_week to
    fit the scope of the model and define a single source of truth for the order of brand & year_week
    '''

    df = df[df['BRAND'].isin(baseConfig['BRANDS'])]
    df = df.sort_values(by=['BRAND', 'YEAR_WEEK'], ascending=True, inplace=False)
    df.reset_index(drop=True, inplace=True)

    return df

def filterByWeeks(feature_df,uniqueWeeks_df, baseConfig, runBackTest, split):
    '''
    Filter dataframe by Weeks to fit the scope of the model defined in the configurations
    '''

    filteredWeeks = uniqueWeeks_df[(uniqueWeeks_df['YEAR_WEEK']== baseConfig['DATA_START']).idxmax():].reset_index()
    filteredWeeks = filteredWeeks[:(filteredWeeks['YEAR_WEEK'] == baseConfig['DATA_END']).idxmax()+1] 

    feature_df = feature_df[(feature_df['YEAR_WEEK'].isin(filteredWeeks['YEAR_WEEK']))].reset_index(drop=True)
    
    if (runBackTest == True):
        feature_df = feature_df[(feature_df['YEAR_WEEK'].isin(split))].reset_index(drop=True)

    return feature_df

def normalizeFeatureDf(baseConfig,responseModelConfig,  feature_df):

    #normalization via saturation parameters according to configurations
    feature_df[baseConfig['TOUCHPOINTS']], touchpoint_norms = HELPER_FUNCTIONS.normalization.normalize_feature(feature_df[baseConfig['TOUCHPOINTS']],feature_df[baseConfig['TOUCHPOINTS']], baseConfig['NORMALIZATION_STEPS_TOUCHPOINTS'])
    
    norm_df = pd.DataFrame()
    for brand in baseConfig['BRANDS']:
        filtFeature_df = feature_df[feature_df['BRAND']==brand]
        #normalization via max, logp1 according to configurations
        filtFeature_df[baseConfig['TARGET']], target_df_norm = HELPER_FUNCTIONS.normalization.normalize_feature(filtFeature_df[baseConfig['TARGET']],filtFeature_df[baseConfig['TARGET']], baseConfig['NORMALIZATION_STEPS_TARGET'])
        norm_df = pd.concat([norm_df, filtFeature_df],axis=0)

    norm_df = norm_df.reset_index()
    return norm_df

def createFeatureDf(baseConfig, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df):
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

    promotion_df = DATA_PREPARATION.promotion.compute_price_discount_feature(sellOut_df.copy(),sellOutDistribution_df.copy(),baseConfig, quantile_reference=0.9)
    feature_df = feature_df.merge(promotion_df[["YEAR_WEEK","BRAND","promotion"]], on=["YEAR_WEEK","BRAND"])
    # promotion_df = pd.read_excel('DATA/CALENDAR_YEAR/comparePromotion.xlsx')
    # promotion_df = promotion_df.replace(['lillet', 'suze','pastis_51','ricard','beefeater','havana_club','absolut','ballantines','chivas_regal','c_campbell','jameson_irish_whisky','aberlour','mumm_champagne'],
    #                                     ['ideal_mouse', 'angry_cat','lully','fast_duck','red_ballon','gold_plane','moistured_bird','visitor','gracious_road','viable_line','silver_coin','heavy_feather','precious_liquid']
    #                                           )

    # feature_df = feature_df.merge(promotion_df[["YEAR_WEEK","BRAND","PR"]], on=["YEAR_WEEK","BRAND"])
    
    
    distribution_df = DATA_PREPARATION.distribution.construct_distribution_feature(sell_out_distribution_df = sellOutDistribution_df.copy(),
                                                                                  configurations = baseConfig,
                                                                                  quantile_reference_level=0)
    feature_df = feature_df.merge(distribution_df[["YEAR_WEEK","BRAND", "distribution"]], on=["YEAR_WEEK","BRAND"])

    epros_df = DATA_PREPARATION.epros.constructEprosFeature(sellOutDistribution_df.copy(), column = 'DISTRIBUTION_FEATURE')
    feature_df = feature_df.merge(epros_df[["YEAR_WEEK","BRAND","epros"]], on=["YEAR_WEEK","BRAND"])

    off_trade_visibility_df = DATA_PREPARATION.distribution.construct_off_trade_visibility_feature(sellOutDistribution_df.copy())
    feature_df = feature_df.merge(off_trade_visibility_df[["YEAR_WEEK","BRAND","off_trade_visibility"]], on=["YEAR_WEEK","BRAND"])

    price_df = DATA_PREPARATION.price.calculatePrice(sellOut_df.copy(), baseConfig)
    feature_df = feature_df.merge(price_df[["YEAR_WEEK","BRAND","AVERAGE_PRICE"]], on=["YEAR_WEEK","BRAND"])

    covid_df= covid_df[['YEAR_WEEK', 'OXFORD_INDEX']].rename(columns={'OXFORD_INDEX':'covid'})
    feature_df = feature_df.merge(covid_df[['YEAR_WEEK','covid']], on='YEAR_WEEK', how='left')
    #covid table does not start until beginning of 2020
    feature_df = feature_df.fillna(0)

    return feature_df

def createNetPriceDf(netPrice_df,baseConfig, filteredFeature_df):

    netPrice_df = netPrice_df[netPrice_df['BRAND'].isin(baseConfig['BRANDS'])]
    netPrice_df = netPrice_df[netPrice_df['SALES_CHANNEL']=='off_trade'].reset_index()
    netPrice_df['NET_PRICE'] = netPrice_df['NET_SALES']/netPrice_df['VOLUME_IN_L']
    netPrice_df = netPrice_df[['FISCAL_YEAR', 'BRAND','NET_PRICE']]

    scope = pd.DataFrame()
    scope['BRAND'] = filteredFeature_df['BRAND'].astype(str)
    scope['YEAR'] = (filteredFeature_df['YEAR_WEEK'].astype(str).str[:4]).astype(int)


    df = scope.merge(netPrice_df, left_on=['YEAR','BRAND'], right_on=['FISCAL_YEAR','BRAND'],how='inner')
   
    
    return df[['BRAND','YEAR','NET_PRICE']]




def run(baseConfig, responseModelConfig, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df, netSales_df, runBackTest,split,name):
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

    
    feature_df = createFeatureDf(baseConfig, mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df)
    
    feature_df = filterByBrands(feature_df.copy(),baseConfig)


    normalizedFeature_df = normalizeFeatureDf(baseConfig,responseModelConfig, feature_df.copy())

    #normalized features require the total scope of weeks since the normalization 
    #is done with maximum values across the entire dataset
    filteredFeature_df = filterByWeeks(feature_df.copy(),uniqueWeeks_df, baseConfig, runBackTest, split)
    normalizedFilteredFeature_df = filterByWeeks(normalizedFeature_df.copy(), uniqueWeeks_df,baseConfig,runBackTest, split)


    netPrice_df = createNetPriceDf(netSales_df,baseConfig, filteredFeature_df)

    #index dataframe to filter other frames based on brand or year specifications (necessary for output generation)
    index_df = filteredFeature_df[['YEAR_WEEK','BRAND']]
    index_df['YEAR'] = index_df['YEAR_WEEK'].astype(str).str[:4]
    


    PYTEST.extractEntryData.extractEntryData(feature_df, 'feature_df', baseConfig['SET_MASTER'])
    PYTEST.extractEntryData.extractEntryData(normalizedFilteredFeature_df, 'normalizedFilteredFeature_df', baseConfig['SET_MASTER'])

    filteredFeature_df.to_excel(f'OUTPUT/{name}/filteredFeature_df.xlsx')
    normalizedFilteredFeature_df.to_excel(f'OUTPUT/{name}/normalizedFilteredFeature_df.xlsx')

    return feature_df, filteredFeature_df, normalizedFeature_df, normalizedFilteredFeature_df, index_df, netPrice_df
