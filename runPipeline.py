import DATA_PREPARATION.mainDataPreparation
import RESPONSE_MODEL.ResponseModel
import RESPONSE_MODEL.stanFile
import BUSINESS_OUTPUT.mainBusinessOutput
import yaml


import pandas as pd

#Define configurations to be used
with open('CONFIG/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

with open('CONFIG/responseModelConfig.yaml', 'r') as file:
            responseModelConfig = yaml.safe_load(file)

with open('CONFIG/outputConfig.yaml', 'r') as file:
            outputConfig = yaml.safe_load(file)
           
#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation


#Create features and prepare data
spendings_df, seasonality_df, price_df, feature_df, control_df, target,index_df = DATA_PREPARATION.mainDataPreparation.run(configurations)


feature_df.to_excel('OUTPUT_DF/feature_df.xlsx')



# Initialize Model instance and Train Bayesian Model 
responseModel = RESPONSE_MODEL.ResponseModel.ResponseModel(index_df = index_df,
                              spendings_df = spendings_df, 
                              seasonality_df = seasonality_df,
                              control_df = control_df, #here it needs to be changed when put togehter with real data
                              configurations = configurations,
                              responseModelConfig= responseModelConfig, 
                              target = target,
                              stanCode = RESPONSE_MODEL.stanFile.stanCode)



#model savings
#WITH COVID
#fast_duck_V1_1
#gold_plane_V1_1

#WITH promotion feature
#fast_duck_V1_2
#gold_plane_V1_2
#

#train bayesian Model
responseModel.runModel(name ='precious_liquid_V1_2_1', load=True)
responseModel.extractParameters(printOut=True)


#calculate contribution decomposition via estimated parameters and original spendings/sales
BUSINESS_OUTPUT.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                           outputConfig = outputConfig,
                                                           price_df = price_df)
''''''