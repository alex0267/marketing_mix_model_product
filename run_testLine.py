import test_suite.data_generation
import test_suite.stan_dict
import test_suite.data_preparation
import Business_Output.main_Business_Output
import helper_functions.hill_function
from Response_Model.main_Response_Model import ResponseModel
import yaml
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
               # {
               #     'control_var':False,
               #     'name':'touchpoint_2',
               #     'beta':1.3 ,
               #     'L':4,
               #     'P':2,
               #     'D':0.9,
               #     'S':1,
               #     'H':1
               #  },
                {
                   'control_var':False,
                   'name':'touchpoint_3',
                   'beta':1.3 ,
                   'L':4,
                   'P':2,
                   'D':0.9,
                   'S':3,
                   'H':1.9
                },
                {
                   'control_var':False,
                   'name':'touchpoint_4',
                   'beta':1.3 ,
                   'L':4,
                   'P':2,
                   'D':0.9,
                   'S':0.7,
                   'H':9.4
                }
               ]

# Create features


#Simulate true response curves
'''
#iterate through lift options (avoid Nan for first by making number close to 0)
lifts = [0.0001, 0.2, 0.4, 0.6, 0.8, 1.0,
 1.2, 1.4, 1.6, 1.8, 2.0,
 2.2, 2.4, 2.6, 2.8, 3.0,
 3.2, 3.4, 3.6, 3.8]

result = []
for lift in lifts:
   data, spendingsFrame, controlFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_shaped',baseSalesCoefficient_tp4=10000*lift, plot = False)
   result.append(data['sales'][0:52].sum())
pd.DataFrame(result).T.to_excel('result.xlsx')
'''
   # print(data['sales'][0:52].sum())
#print(data)

# data, spendingsFrame, controlFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_shaped',baseSalesCoefficient_tp3=10000, plot = False)
# print(data['sales'][0:52].sum())

data, spendingsFrame, controlFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_shaped',plot = False)
   
# Prepare data
feature_df = test_suite.data_preparation.normalize_data(spendingsFrame, target = data['sales'])

seasonality_df = controlFrame[configurations['SEASONALITY_VARIABLES_BASE']]
control_df = controlFrame[configurations['CONTROL_VARIABLES_BASE']]


#Initialize Model instance and Train Bayesian Model 
responseModel = ResponseModel(spendingsFrame = spendingsFrame, 
                              controlFrame = control_df,
                              seasonalityFrame = seasonality_df,
                              configurations = configurations, 
                              data_normalized = feature_df, 
                              target = data['sales'])

   #Create dictionary
stanDict = test_suite.stan_dict.createDict(responseModel, max_lag)
responseModel.stanDict = stanDict

print('standict')
print(stanDict)

#tp_4 shaped model: test_shape_7
#tp_3 shaped model: tp_3_shaped_model
#tp_3 & tp_4 shaped model: tp_3_tp_4_shaped_model


   #train bayesian Model
responseModel.runModel(name ='test', load=False)
responseModel.extractParameters(printOut=True)
'''
#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.main_Business_Output.createBusinessOutputs(responseModel = responseModel)
'''