import Data_Preparation.mainDataPreparation
import Response_Model.ResponseModel
import Response_Model.stanFile
import Business_Output.mainBusinessOutput
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
spendings_df, seasonality_df, price_df, feature_df, control_df, target,index_df = Data_Preparation.mainDataPreparation.run(configurations)


feature_df.to_excel('output_df/feature_df.xlsx')



# Initialize Model instance and Train Bayesian Model 
responseModel = Response_Model.ResponseModel.ResponseModel(index_df = index_df,
                              spendings_df = spendings_df, 
                              seasonality_df = seasonality_df,
                              control_df = control_df, #here it needs to be changed when put togehter with real data
                              configurations = configurations,
                              responseModelConfig= responseModelConfig, 
                              target = target,
                              stanCode = Response_Model.stanFile.stanCode)



#model savings
#true_data_adstocked_shaped_v01 - angry cat model
#true_data_adstocked_shaped_fast_duck - fast_duck model
#first_attemps_V02 : First try of implementing the model
#first_attemps_V03 : As in first_attemps_V02 but with adstock = 4 instead of 8
#first_attemps_V04_fast_duck: included control feature capability
#V05_fast_duck: no limits on shape and slope
#first_attemps_V04_precious_liquid : same with champagne
#first_attemps_V05_precious_liquid : = 04 but with changes naming convention
#first_attemps_V06_precious_liquid : with covid
#fast_duck_V1_1
#gold_plane_V1_1

#train bayesian Model
responseModel.runModel(name ='gold_plane_V1_1', load=False)
responseModel.extractParameters(printOut=True)


#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.mainBusinessOutput.createBusinessOutputs(responseModel = responseModel, 
                                                           outputConfig = outputConfig,
                                                           price_df = price_df)
''''''