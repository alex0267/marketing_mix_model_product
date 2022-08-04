import helper_functions.transformations
import numpy as np
import yaml
import pandas as pd
import openpyxl

def createDict(feature_df, max_lag):

    with open('config/baseConfig.yaml', 'r') as file:
        configurations = yaml.safe_load(file)

        num_media = len(configurations['TOUCHPOINTS'])

        X_media = feature_df[configurations['TOUCHPOINTS']]
        X_media = np.concatenate((np.zeros((max_lag-1, num_media)), np.array(X_media)),axis=0)

        seasonalityFrame = feature_df[configurations['SEASONALITY_VARIABLES_BASE']]
        controlFrame = feature_df[configurations['CONTROL_VARIABLES_BASE']]

    stanDict = {
        'N': len(feature_df),
        'max_lag': max_lag, 
        'num_media': num_media,
        'X_media': X_media,
        'seasonality': np.array(seasonalityFrame),
        'control': np.array(controlFrame), 
        'y': feature_df['TARGET_VOL_SO'].values
    }

    return stanDict