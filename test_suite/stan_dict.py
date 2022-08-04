import helper_functions.transformations
import numpy as np
import yaml

def createDict(feature_df, controlData, original_sales, max_lag):

    with open('test_suite/baseConfig.yaml', 'r') as file:
        configurations = yaml.safe_load(file)

        num_media = len(configurations['TOUCHPOINTS'])
        X_media = feature_df[configurations['TOUCHPOINTS']]
        X_media = np.concatenate((np.zeros((max_lag-1, num_media)), np.array(X_media)),axis=0)

        seasonalityFrame = controlData[configurations['SEASONALITY_VARIABLES_BASE']]
        controlFrame = controlData[configurations['CONTROL_VARIABLES_BASE']]



    stanDict = {
        'N': len(feature_df),
        'max_lag': max_lag, 
        'num_media': num_media,
        'X_media': X_media,
        'seasonality': np.array(seasonalityFrame),
        'control': np.array(controlFrame),
        'y': feature_df['sales'].values
    }

    return stanDict