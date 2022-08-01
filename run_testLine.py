import test_suite.data_generation
import test_suite.stan_dict
import test_suite.data_preparation
from Response_Model.main_Response_Model import ResponseModel
import yaml


#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation

#Define test format

#Define configurations to be used
with open('test_suite/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

#maximum number of weeks the touchpoint can influence sales
max_lag = 4

#touchpoint definition
touchpoints = [
               {
                   'name':'touchpoint_2',
                   'beta':1.3 ,
                   'L':4,
                   'P':2,
                   'D':0.9
                },
                {
                   'name':'touchpoint_3',
                   'beta':1.3 ,
                   'L':4,
                   'P':2,
                   'D':0.9
                }
               ]

#Create features
data, spendingsFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_adstocked')


#Prepare data
feature_df = test_suite.data_preparation.normalize_data(data, spendingsFrame)

#create stan dictionary
stanDict = test_suite.stan_dict.createDict(feature_df, max_lag)

#Initialize Model instance and Train Bayesian Model
responseModel = ResponseModel(stanDict, configurations)
responseModel.runModel(load=False)
responseModel.extractParameters()



