import Data_Preparation.main_Data_Preparation
import Response_Model.main_Response_Model
import Response_Model.stanDict
import stan
from Response_Model.main_Response_Model import ResponseModel
import Business_Output.decompose_contribution
import yaml

import pandas as pd

#Define configurations to be used
with open('config/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation

max_lag=8

#Create features and prepare data
spendings_df, feature_df, feature_df_normalized, seasonality_df, promotion_df, target = Data_Preparation.main_Data_Preparation.run()
feature_df_normalized.to_csv('feature_df_norm.csv')



# Initialize Model instance and Train Bayesian Model 
responseModel = ResponseModel(spendingsFrame = spendings_df, 
                              controlFrame = promotion_df,
                              seasonalityFrame = seasonality_df,
                              configurations = configurations, 
                              data_normalized = feature_df_normalized, 
                              target = target)


   #Create dictionary
stanDict = Response_Model.stanDict.createDict(responseModel, max_lag)
responseModel.stanDict = stanDict


 #train bayesian Model
responseModel.runModel(name ='true_data_adstocked_shaped_v01', load=False)
responseModel.extractParameters(printOut=True)

'''
#Initialize Model instance and Train Bayesian Model
responseModel = ResponseModel(stanDict, configurations, feature_df, target_raw)
responseModel.runModel(name ='real_data', load=True)
responseModel.extractParameters(printOut=True)

#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel, feature_df, target_raw, plot=False)



'''