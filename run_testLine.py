import test_suite.data_generation
import test_suite.stan_dict
import test_suite.data_preparation
import Business_Output.decompose_contribution
from Response_Model.main_Response_Model import ResponseModel
import yaml
import numpy as np

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
                  'control_var':'month',
                  'name':'december',
                  'factor': 6000,
                  'beta':1
               },
               {
                  'control_var':'month',
                  'name':'november',
                  'factor': 4000,
                  'beta':1
               },
               {
                  'control_var':'month',
                  'name':'june',
                  'factor': -3000,
                  'beta':1
               },
               {
                  'control_var':'month',
                  'name':'july',
                  'factor': -3000,
                  'beta':1
               },
               {
                  'control_var':False,
                  'name':'base_1',
                  'factor': 30000,
                  'noise_percentage': 0.1,
                  'beta':1
               },
               {
                   'control_var':False,
                   'name':'touchpoint_2',
                   'beta':1.3 ,
                   'L':4,
                   'P':2,
                   'D':0.9
                },
                {
                   'control_var':False,
                   'name':'touchpoint_3',
                   'beta':1.3 ,
                   'L':4,
                   'P':2,
                   'D':0.9
                }
               ]

#Create features
data, spendingsFrame, controlFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_adstocked')

#print('here')
print(controlFrame)


#Prepare data
feature_df = test_suite.data_preparation.normalize_data(data, spendingsFrame)

#create stan dictionary
stanDict = test_suite.stan_dict.createDict(feature_df, controlFrame, max_lag)

#Initialize Model instance and Train Bayesian Model
responseModel = ResponseModel(stanDict, configurations)
responseModel.runModel(load=True)
responseModel.extractParameters(printOut=True)
print('here')
print(responseModel.parameters)
print(responseModel.beta_seasonality)

#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel, feature_df, data['sales'], plot=True)