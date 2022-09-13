import Data_Preparation.main_Data_Preparation
import Response_Model.main_Response_Model
from Response_Model.main_Response_Model import ResponseModel
import Response_Model.stan_file
import Business_Output.main_Business_Output
import yaml


import pandas as pd

#Define configurations to be used
with open('config/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

with open('config/responseModelConfig.yaml', 'r') as file:
            responseModelConfig = yaml.safe_load(file)

with open('config/outputConfig.yaml', 'r') as file:
            outputConfig = yaml.safe_load(file)
            
#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation


#Create features and prepare data
spendings_df, feature_df, seasonality_df, promotion_df, target = Data_Preparation.main_Data_Preparation.run()
#print(feature_df)
feature_df.to_csv('feature_df.csv')

'''
# Initialize Model instance and Train Bayesian Model 
responseModel = ResponseModel(spendingsFrame = spendings_df, 
                              controlFrame = promotion_df, #here it needs to be changed when put togehter with real data
                              seasonalityFrame = seasonality_df,
                              configurations = configurations,
                              responseModelConfig= responseModelConfig, 
                              target = target,
                              stan_code = Response_Model.stan_file.stan_code)


#model savings
#true_data_adstocked_shaped_v01 - angry cat model
#true_data_adstocked_shaped_fast_duck - fast_duck model

 #train bayesian Model
responseModel.runModel(name ='true_data_adstocked_shaped_fast_duck', load=True)
responseModel.extractParameters(printOut=True)

#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.main_Business_Output.createBusinessOutputs(responseModel = responseModel, 
                                                           responseCurveConfig = responseCurveConfig)


'''