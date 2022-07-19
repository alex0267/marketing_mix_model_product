import Data_Preparation.main_Data_Preparation
import Response_Model.main_Response_Model
import pystan

#lets hope this works -> Parameter for stan model
# (requirement according to TDS article)

import os
os.environ['CC'] = 'gcc-10'
os.environ['CXX'] = 'g++-10'

#Run pipeline tasks:
# - Data Preparation
# - Short-term Response Model Training
# - Output Generation

#Create features and prepare data
feature_df = Data_Preparation.main_Data_Preparation.run()
print(feature_df)

#Train Bayesian Model
Response_Model.main_Response_Model.run(feature_df)

