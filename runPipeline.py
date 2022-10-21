import DATA_PREPARATION.mainDataPreparation
import RESPONSE_MODEL.ResponseModel
import RESPONSE_MODEL.stanFile
import BUSINESS_OUTPUT.mainBusinessOutput
import DATA_PREPARATION.loadData
import yaml


import pandas as pd




def run():
    '''
    Execution of main MMM pipeline:
        - Data Loading
        - Data Preparation
        - Short-term Response Model Training
        - Output Generation
    '''

    #Define configurations to be used
    with open('CONFIG/baseConfig.yaml', 'r') as file:
                configurations = yaml.safe_load(file)

    with open('CONFIG/responseModelConfig.yaml', 'r') as file:
                responseModelConfig = yaml.safe_load(file)

    with open('CONFIG/outputConfig.yaml', 'r') as file:
                outputConfig = yaml.safe_load(file)
    
    
    mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df = DATA_PREPARATION.loadData.loadData()


    #Create features and prepare data
    feature_df, filteredFeature_df, normalizedFeature_df, normalizedFilteredFeature_df, index_df = DATA_PREPARATION.mainDataPreparation.run(configurations = configurations,
                                                                                                                    responseModelConfig =  responseModelConfig,
                                                                                                                    mediaExec_df = mediaExec_df.copy(),
                                                                                                                    sellOut_df = sellOut_df.copy(),
                                                                                                                    sellOutDistribution_df = sellOutDistribution_df.copy(),
                                                                                                                    sellOutCompetition_df = sellOutCompetition_df.copy(),
                                                                                                                    covid_df = covid_df.copy(),
                                                                                                                    uniqueWeeks_df = uniqueWeeks_df.copy())

    feature_df.to_excel('OUTPUT_DF/feature_df.xlsx')
    filteredFeature_df.to_excel('OUTPUT_DF/filteredFeature_df.xlsx')
    normalizedFeature_df.to_excel('OUTPUT_DF/normalizedFeature_df.xlsx')
    normalizedFilteredFeature_df.to_excel('OUTPUT_DF/normalizedFilteredFeature_df.xlsx')
    index_df.to_excel('OUTPUT_DF/index_df.xlsx')


    price_df = filteredFeature_df['AVERAGE_PRICE']
    seasonality_df = filteredFeature_df[configurations['SEASONALITY_VARIABLES_BASE']]
    spendings_df = filteredFeature_df[configurations['TOUCHPOINTS']]
    target = filteredFeature_df[configurations['TARGET']]
    control_df = filteredFeature_df[['YEAR_WEEK','BRAND','distribution', 'promotion', 'epros', 'covid','off_trade_visibility']]

    # Initialize Model instance and Train Bayesian Model 
    responseModel = RESPONSE_MODEL.ResponseModel.ResponseModel(configurations = configurations,
                                                        responseModelConfig= responseModelConfig,
                                                        feature_df = feature_df,
                                                        filteredFeature_df = filteredFeature_df,
                                                        normalizedFeature_df = normalizedFeature_df,
                                                        normalizedFilteredFeature_df = normalizedFilteredFeature_df,
                                                        index_df = index_df,
                                                        stanCode = RESPONSE_MODEL.stanFile.stanCode)


    #model savings

    #all custom
    #test -> is fast_duck
    #gold_plane_V1_9
    #precious_liquid_V1_9

    #all custom + epros
    #fast_duck_V1_10
    #gold_plane_V1_10
    #precious_liquid_V1_10

    #all custom + loyality card
    #fast_duck_V1_11
    #gold_plane_V1_11
    #precious_liquid_V1_11

    #off trade
    #fast_duck_V1_12
    #gold_plane_V1_12
    #precious_liquid_V1_12

    #testing
    #fast_duck_V1_TEST - all good version

    
    responseModel.runModel(name ='fast_duck_V1_TEST_2010', load=True)
    responseModel.extractParameters(printOut=True)
    
    #calculate contribution decomposition via estimated parameters and original spendings/sales
    BUSINESS_OUTPUT.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                            outputConfig = outputConfig,
                                                            price_df = price_df)
    '''
    '''

run()