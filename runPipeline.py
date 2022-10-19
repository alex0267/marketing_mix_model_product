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
    
    
    mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks = DATA_PREPARATION.loadData.loadData()


    #Create features and prepare data
    spendings_df, seasonality_df, price_df, feature_df, target,index_df, control_df = DATA_PREPARATION.mainDataPreparation.run(configurations = configurations,
                                                                                                                    responseModelConfig =  responseModelConfig,
                                                                                                                    mediaExec_df = mediaExec_df.copy(),
                                                                                                                    sellOut_df = sellOut_df.copy(),
                                                                                                                    sellOutDistribution_df = sellOutDistribution_df.copy(),
                                                                                                                    sellOutCompetition_df = sellOutCompetition_df.copy(),
                                                                                                                    covid_df = covid_df.copy(),
                                                                                                                    uniqueWeeks = uniqueWeeks.copy())
    print('here')
    print(control_df)
    print(feature_df)
    feature_df.to_excel('OUTPUT_DF/feature_df.xlsx')



    # Initialize Model instance and Train Bayesian Model 
    responseModel = RESPONSE_MODEL.ResponseModel.ResponseModel(index_df = index_df,
                                spendings_df = spendings_df, 
                                seasonality_df = seasonality_df,
                                control_df = control_df,
                                configurations = configurations,
                                responseModelConfig= responseModelConfig, 
                                target = target,
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


    
    responseModel.runModel(name ='fast_duck_V1_TEST', load=False)
    responseModel.extractParameters(printOut=True)

    #calculate contribution decomposition via estimated parameters and original spendings/sales
    BUSINESS_OUTPUT.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                            outputConfig = outputConfig,
                                                            price_df = price_df)
    ''''''

run()