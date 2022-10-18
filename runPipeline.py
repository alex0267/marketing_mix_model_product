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
spendings_df, seasonality_df, price_df, feature_df, control_df, target,index_df = DATA_PREPARATION.mainDataPreparation.run(configurations, responseModelConfig)


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

# shape[i] ~ gamma(4,4); scale[i] beta(2,2); priors according to PR model
#train bayesian Model
#fast_duck_V1_6
#gold_plane_V1_6
#precious_liquid_V1_6

#include promotion periods
# precious_liquid_V1_7
#fast_duck_V1_7

#change norm to exclude saturation
#fast_duck_V1_8
#gold_plane_V1_8

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

responseModel.runModel(name ='precious_liquid_V1_12', load=False)
responseModel.extractParameters(printOut=True)


#calculate contribution decomposition via estimated parameters and original spendings/sales
BUSINESS_OUTPUT.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                           outputConfig = outputConfig,
                                                           price_df = price_df)
''''''