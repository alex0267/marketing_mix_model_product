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
#print(feature_df)


#print(price_df.get_group(('angry_cat', '2019')))
# print(price_df[price_df['BRAND']=='angry_cat' and price_df['YEAR']=='2019']  )

#print(spendings_df)
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
#true_data_adstocked_shaped_v01 - angry cat model
#true_data_adstocked_shaped_fast_duck - fast_duck model
#first_attemps_V02 : First try of implementing the model
#first_attemps_V03 : As in first_attemps_V02 but with adstock = 4 instead of 8

 #train bayesian Model
responseModel.runModel(name ='first_attemps_V03', load=True)
responseModel.extractParameters(printOut=True)

#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.main_Business_Output.createBusinessOutputs(responseModel = responseModel, 
                                                           outputConfig = outputConfig,
                                                           price_df = price_df)
