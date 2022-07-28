import test_suite.data_generation
import test_suite.stan_dict
from Response_Model.main_Response_Model import ResponseModel

#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation

#Define test format

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

#Create features and prepare data
data, spendingsFrame = test_suite.data_generation.simulateTouchpoints(touchpoints,'_adstocked')
stanDict = test_suite.stan_dict.createDict(data, spendingsFrame)

#Train Bayesian Model
responseModel = ResponseModel(touchpoints, stanDict)
responseModel.runModel(load=True)




