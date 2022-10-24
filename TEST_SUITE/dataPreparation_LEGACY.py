# import Data_Preparation.normalization
# import yaml
# import pandas as pd

# def normalize_data(spendingsFrame, target = None):


#     with open('test_suite/baseConfig.yaml', 'r') as file:
#         configurations = yaml.safe_load(file)
#         feature_df = pd.DataFrame()

#         for touchpoint in configurations['TOUCHPOINTS']:

#             #define the type of normalization(s) to apply defined in config 'NORMALIZATION_STEPS_TOUCHPOINTS':
#             # First we apply the max/custom normalization
#             # Second we do the log transformation for each touchpoint
#             normalization_steps = configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint]

#             #send the column to the normalization file with all required parameters
#             feature_df[touchpoint] = Data_Preparation.normalization.normalize_feature(spendingsFrame, normalization_steps, configurations, touchpoint)
        
        
#         #normalize and log transform sales
#         if target is not None:
#             feature_df['sales'] = Data_Preparation.normalization.normalize_feature(target, configurations['NORMALIZATION_STEPS_SALES']['sales'], configurations, 'sales')

#     return feature_df
