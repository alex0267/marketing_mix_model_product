import test_suite.data_generation
import test_suite.data_preparation
import Business_Output.main_Business_Output
from Response_Model.main_Response_Model import ResponseModel
import Response_Model.stan_file
import yaml
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation

#Define test format

#Define configurations to be used
with open('test_suite/baseConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

with open('test_suite/responseModelConfig.yaml', 'r') as file:
            responseModelConfig = yaml.safe_load(file)

with open('test_suite/outputConfig.yaml', 'r') as file:
      outputConfig = yaml.safe_load(file)

#touchpoint definition
touchpoints = [
               # {
               #    'control_var':'month',
               #    'name':'december',
               #    'factor': 6000,
               #    'beta':1
               # },
               # {
               #    'control_var':'month',
               #    'name':'november',
               #    'factor': 4000,
               #    'beta':1
               # },
               # {
               #    'control_var':'month',
               #    'name':'june',
               #    'factor': -3000,
               #    'beta':1
               # },
               # {
               #    'control_var':'month',
               #    'name':'july',
               #    'factor': -3000,
               #    'beta':1
               # },
               {
                  'control_var':False,
                  'name':'base_1',
                  'factor': 30000,
                  'noise_percentage': 0,
                  'beta':1,
                  'sales_saturation':1
               },

               {
                   'control_var':False,
                   'name':'touchpoint_5',
                   'beta':1,
                   'L':4,
                   'D':0.8,
                   'scale':1.8,
                   'shape':1,
                   'saturation':5000,
                   'threshold':0,
                   'sales_saturation':10000,
               },
                              {
                   'control_var':False,
                   'name':'touchpoint_6',
                   'beta':1,
                   'L':4,
                   'D':0.4,
                   'scale':0.7,
                   'shape':2,
                   'saturation':6000,
                   'threshold':0,
                   'sales_saturation':20000,
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

data, price_df, spendingsFrame, controlFrame, indexColumns = test_suite.data_generation.simulateTouchpoints(touchpoints, configurations, responseModelConfig, '_shaped',plot = True)


#Initialize Model instance and Train Bayesian Model 
responseModel = ResponseModel(indexColumns = indexColumns,
                              spendingsFrame = spendingsFrame, 
                              controlFrame = controlFrame,
                              configurations = configurations,
                              responseModelConfig=responseModelConfig, 
                              target = data['sales'],
                              stan_code = Response_Model.stan_file.stan_code)



# for key in stanDict.keys():
#    print(key)
#    print(stanDict[key])
#    if type(stanDict[key]) is not int:
#       print('shape')
#       print((stanDict[key]).shape)

#tp_4 shaped model: test_shape_7
#tp_3 shaped model: tp_3_shaped_model
#tp_3 & tp_4 shaped model: tp_3_tp_4_shaped_model

#NEW MODEL
#test: test of new adstock & shape with tp_5
#One touchpoint - adstock_shape_v02
#Two touchpoints - 2tps_adstock_shape_v01
#Two touchpoints, different initialization of data generation of tp_6 - 2tps_adstock_shape_v02
#As tps_adstock_shape_v02 but with baseline
#2tps_adstock_shape_v04:As tps_adstock_shape_v03 but without noise
#2tps_adstock_shape_v05:As tps_adstock_shape_v04 but touchpoint_5 has threshold 3000 and saturation 10000 (before saturation was equal to the norm (max_tp_spend) = 6250)
#2tps_adstock_shape_v06: as in tps_adstock_shape_v03 but with adapted staturation and threshold definition
#2tps_adstock_shape_v07: as in tps_adstock_shape_v04 but with adapted saturation and threshold definition

   #train bayesian Model
responseModel.runModel(name ='2tps_adstock_shape_v08', load=True)
responseModel.extractParameters(printOut=False)


#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.main_Business_Output.createBusinessOutputs(responseModel = responseModel, 
                                                           outputConfig = outputConfig,
                                                           price_df = price_df)


