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
spendings_df, price_df, feature_df, control_df, target,indexColumns = Data_Preparation.main_Data_Preparation.run(configurations)



feature_df.to_csv('feature_df.csv')

# Initialize Model instance and Train Bayesian Model 
responseModel = ResponseModel(indexColumns = indexColumns,
                              spendingsFrame = spendings_df, 
                              controlFrame = control_df, #here it needs to be changed when put togehter with real data
                              configurations = configurations,
                              responseModelConfig= responseModelConfig, 
                              target = target,
                              stan_code = Response_Model.stan_file.stan_code)



#model savings

 #train bayesian Model
responseModel.runModel(name ='first_attemps_V03', load=True)
responseModel.extractParameters(printOut=True)

#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.main_Business_Output.createBusinessOutputs(responseModel = responseModel, 
                                                           outputConfig = outputConfig,
                                                           price_df = price_df)
