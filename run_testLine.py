import test_suite.data_generation
import test_suite.stan_dict
import test_suite.data_preparation
import Business_Output.decompose_contribution
import helper_functions.hill_function
from Response_Model.main_Response_Model import ResponseModel
import yaml
import numpy as np
import matplotlib.pyplot as plt

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
               #  {
               #     'control_var':False,
               #     'name':'touchpoint_3',
               #     'beta':1.3 ,
               #     'L':4,
               #     'P':2,
               #     'D':0.9,
               #     'S':3,
               #     'H':1.9
               #  },
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
data, spendingsFrame, controlFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_shaped')

print(data)

# rangeHill = np.arange(0, 10.1, 0.1).tolist()

# data = [x for x in (rangeHill)]

# hill = helper_functions.hill_function.hill_function(rangeHill, 1.3,3.5)


# plt.plot(rangeHill, hill)
# plt.savefig('hill2.png')


# Prepare data
feature_df = test_suite.data_preparation.normalize_data(data, spendingsFrame)

#Create dictionary

stanDict = test_suite.stan_dict.createDict(feature_df, controlFrame, data['sales'], spendingsFrame, max_lag)

#Initialize Model instance and Train Bayesian Model 
responseModel = ResponseModel(stanDict, configurations, feature_df, data['sales'])

#first shape test: 'test_diff_touchpoints'
#second shape test: 'test_shape_2'
   #resuts in parameters of shape that are comparable to the true shape parameters
   #However, relatively inaccurate

#third shape test: 'test_shape_3'
   #results in weird shape parameters
   #However, relatively high accuracy??
   #Not clear what changed from 2 to 3 (some transformation definitions in stan file)

#third shape test: 'test_shape_4'
   #Changed to _shaped -> error in data generation until here
#fourth shape test: 'test_shape_5'
   #Without *2

#test_shape_5
   #change prior from N (0,1) to ()

#test_shape_6
   #change of tp_3 from S:3.5, H:5,2 to 3 , 1.9

#test_shape_7
   #only kept TP_4
responseModel.runModel(name ='test_shape_7', load=True)
responseModel.extractParameters(printOut=True)

#calculate contribution decomposition via estimated parameters and original spendings/sales
Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel, spendingsFrame, data['sales'],data, plot=True)
