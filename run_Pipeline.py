import Data_Preparation.main_Data_Preparation
import Response_Model.main_Response_Model
import Response_Model.stanDict
import stan
from Response_Model.main_Response_Model import ResponseModel
import yaml

#Define configurations to be used
with open('config/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation

max_lag=8

#Create features and prepare data
feature_df = Data_Preparation.main_Data_Preparation.run()
feature_df.to_csv('feature_df2.csv')
print(feature_df.min())

#create stan dictionary
stanDict = Response_Model.stanDict.createDict(feature_df, max_lag)
print(stanDict)

#Initialize Model instance and Train Bayesian Model
responseModel = ResponseModel(0,stanDict, configurations)
responseModel.runModel(load=True)
responseModel.extractParameters()

