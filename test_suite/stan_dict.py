import helper_functions.transformations
import numpy as np

def createDict(data, spendingsFrame):
    df_mmm, sc_mmm = helper_functions.transformations.mean_log1p_trandform(data, ['sales'])
    mu_touchpoints = spendingsFrame.mean().values
    max_lag = 4
    num_media = len(spendingsFrame.columns)
    X_media = np.concatenate((np.zeros((max_lag-1, num_media)), np.array(spendingsFrame)),axis=0)


    stanDict = {
        'N': len(data),
        'max_lag': max_lag, 
        'num_media': num_media,
        'X_media': X_media, 
        'mu_mdip': mu_touchpoints,
        'y': df_mmm['sales'].values
    }

    return stanDict