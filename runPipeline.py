import DATA_PREPARATION.mainDataPreparation
import RESPONSE_MODEL.ResponseModel
import RESPONSE_MODEL.stanModel
import BUSINESS_OUTPUT.mainBusinessOutput
import DATA_PREPARATION.dataLoader
import PYTEST.mainComparisonTests

import yaml
import pandas as pd
import os


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
                baseConfig = yaml.safe_load(file)

    with open('CONFIG/responseModelConfig.yaml', 'r') as file:
                responseModelConfig = yaml.safe_load(file)

    with open('CONFIG/outputConfig.yaml', 'r') as file:
                outputConfig = yaml.safe_load(file)
    
    
    outputName = f'{name}_{str(load)}'

    path = f'OUTPUT/{outputName}'
    if not os.path.isdir(path):
        os.mkdir(path)
    
    
    mediaExec_df, sellOut_df, sellOutDistribution_df, sellOutCompetition_df, covid_df, uniqueWeeks_df, filteredUniqueWeeks_df,netSales_df = DATA_PREPARATION.dataLoader.loadData(baseConfig)


    #Create features and prepare data
    feature_df, filteredFeature_df, normalizedFeature_df, normalizedFilteredFeature_df, index_df, netPrice_df = DATA_PREPARATION.mainDataPreparation.run(baseConfig = baseConfig,
                                                                                                                    responseModelConfig =  responseModelConfig,
                                                                                                                    mediaExec_df = mediaExec_df.copy(),
                                                                                                                    sellOut_df = sellOut_df.copy(),
                                                                                                                    sellOutDistribution_df = sellOutDistribution_df.copy(),
                                                                                                                    sellOutCompetition_df = sellOutCompetition_df.copy(),
                                                                                                                    covid_df = covid_df.copy(),
                                                                                                                    uniqueWeeks_df = uniqueWeeks_df.copy(),
                                                                                                                    netSales_df = netSales_df.copy(),
                                                                                                                    runBackTest = runBackTest,
                                                                                                                    split = split,
                                                                                                                    name = outputName)

    

    # Initialize Model instance and Train Bayesian Model 
    responseModel = RESPONSE_MODEL.ResponseModel.ResponseModel(baseConfig = baseConfig,
                                                        responseModelConfig= responseModelConfig,
                                                        feature_df = feature_df,
                                                        filteredFeature_df = filteredFeature_df,
                                                        normalizedFeature_df = normalizedFeature_df,
                                                        normalizedFilteredFeature_df = normalizedFilteredFeature_df,
                                                        index_df = index_df,
                                                        stanCode = RESPONSE_MODEL.stanModel.stanCode)
    
    #checkpoint test
    #PYTEST.mainComparisonTests.compareEntryData()
    
    #model savings

    #CAL_7_BRANDS_NEW_SATURATIONS
    #CAL_7_BRANDS_NEW_SATURATIONS_NO_SHIFT
    #ALL_BRANDS_V01
    

    
    responseModel.runModel(name =name,outputName = outputName, load=load)
    responseModel.extractParameters(printOut=False)
    
    
    #calculate contribution decomposition via estimated parameters and original spendings/sales
    r2 = BUSINESS_OUTPUT.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                                  outputConfig = outputConfig,
                                                                  price_df = netPrice_df,
                                                                  name = outputName)
    
    #run tests
    #print('running tests ...')
    #PYTEST.mainComparisonTests.runComparisonTests() 
    print(f'r2 collection: {r2}')
    return r2
    
    
    
    ''''''
run(name = 'ALL_BRANDS_V01',load=True)
