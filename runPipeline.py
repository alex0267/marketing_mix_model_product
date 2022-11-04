import DATA_PREPARATION.mainDataPreparation
import RESPONSE_MODEL.ResponseModel
import RESPONSE_MODEL.stanFile
import RESPONSE_MODEL.stan2
import BUSINESS_OUTPUT.mainBusinessOutput
import DATA_PREPARATION.dataLoader
import PYTEST.mainComparisonTests

import yaml
import pandas as pd


def run(runBackTest=False, split = False, name = False, load = True):
    
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
    
    
    mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df, filteredUniqueWeeks_df = DATA_PREPARATION.dataLoader.loadData(configurations)


    #Create features and prepare data
    feature_df, filteredFeature_df, normalizedFeature_df, normalizedFilteredFeature_df, index_df = DATA_PREPARATION.mainDataPreparation.run(configurations = configurations,
                                                                                                                    responseModelConfig =  responseModelConfig,
                                                                                                                    mediaExec_df = mediaExec_df.copy(),
                                                                                                                    sellOut_df = sellOut_df.copy(),
                                                                                                                    sellOutDistribution_df = sellOutDistribution_df.copy(),
                                                                                                                    sellOutCompetition_df = sellOutCompetition_df.copy(),
                                                                                                                    covid_df = covid_df.copy(),
                                                                                                                    uniqueWeeks_df = uniqueWeeks_df.copy(),
                                                                                                                    runBackTest = runBackTest,
                                                                                                                    split = split)



    price_df = filteredFeature_df['AVERAGE_PRICE']

    
    # Initialize Model instance and Train Bayesian Model 
    responseModel = RESPONSE_MODEL.ResponseModel.ResponseModel(configurations = configurations,
                                                        responseModelConfig= responseModelConfig,
                                                        feature_df = feature_df,
                                                        filteredFeature_df = filteredFeature_df,
                                                        normalizedFeature_df = normalizedFeature_df,
                                                        normalizedFilteredFeature_df = normalizedFilteredFeature_df,
                                                        index_df = index_df,
                                                        stanCode = RESPONSE_MODEL.stan2.stanCode)

    #checkpoint test
    #PYTEST.mainComparisonTests.compareEntryData()
    
    #model savings

    #off trade
    #fast_duck_V1_12
    #gold_plane_V1_12
    #precious_liquid_V1_12


    #fast_duck_V1_TEST_2010 - should also be good version (contains test of mary merged)
    #fast_duck_V1_TEST_2010_2_SAME - Same for comparison of variability
    #fast_duck_V1_TEST_2010_3_SAME


    #first attempt in multi brand vectorized version - all still one brand but brand capability is built in
    #test_multi-vector
    # test_multi-vector03 - first successful run, but results are wrong
    # test_multi-vector04 - now changed the adstock to beginning - still wrong
    # test_multi-vector05 - trying stuff
    
    responseModel.runModel(name =name, load=load)
    responseModel.extractParameters(printOut=False)
    
    outputName = f'{name}_{str(load)}'
    
    #calculate contribution decomposition via estimated parameters and original spendings/sales
    r2 = BUSINESS_OUTPUT.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                                  outputConfig = outputConfig,
                                                                  price_df = price_df,
                                                                  name = outputName)
    
    #run tests
    #print('running tests ...')
    #PYTEST.mainComparisonTests.runComparisonTests() 

    return r2
    
    ''''''
run(name = 'test_multi-vector05',load=False)
# print(f'r2: {r2}')

