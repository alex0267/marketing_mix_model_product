import helper_functions.transformations
import numpy as np
import yaml
import pandas as pd
import openpyxl




#Dictionary should be entirely be created based on responseModel class objects since its so closely related
def createDict(responseModel, max_lag):

    configurations = responseModel.configurations

    num_media = len(configurations['TOUCHPOINTS'])
    media_norm = np.array(responseModel.spendingsFrame[configurations['TOUCHPOINTS']].max())
    # X_media = feature_df[configurations['TOUCHPOINTS']]
    X_media = responseModel.spendingsFrame[configurations['TOUCHPOINTS']]
    X_media = np.concatenate((np.zeros((max_lag-1, num_media)), np.array(X_media)),axis=0)


    stanDict = {
        'N': len(responseModel.data_normalized),
        'max_lag': max_lag, 
        'num_media': num_media,
        'X_media': X_media,
        'media_norm': media_norm,
        'seasonality': np.array(responseModel.seasonality_df),
        # 'control': np.array(responseModel.otherControl_df),
        'y': responseModel.data_normalized['TARGET_VOL_SO'].values
    }

    return stanDict


'''
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
'''