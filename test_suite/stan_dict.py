import helper_functions.transformations
import numpy as np
import yaml


#Dictionary should be entirely be created based on responseModel class objects since its so closely related
def createDict(responseModel, max_lag):

    configurations = responseModel.configurations

    num_media = len(configurations['TOUCHPOINTS'])
    media_norm = np.array(responseModel.spendingsFrame[configurations['TOUCHPOINTS']].max())
    # X_media = feature_df[configurations['TOUCHPOINTS']]
    X_media = responseModel.spendingsFrame[configurations['TOUCHPOINTS']]
    X_media = np.concatenate((np.zeros((max_lag-1, num_media)), np.array(X_media)),axis=0)

    print()
    stanDict = {
        'N': len(responseModel.data_normalized),
        'max_lag': max_lag, 
        'num_media': num_media,
        'X_media': X_media,
        'media_norm': media_norm,
        'seasonality': np.array(responseModel.seasonality_df),
        'control': np.array(responseModel.otherControl_df),
        'y': responseModel.data_normalized[configurations['TARGET']].values
    }

    return stanDict