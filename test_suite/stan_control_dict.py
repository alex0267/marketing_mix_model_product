import helper_functions.transformations
import numpy as np

def createDict(feature_df, controlFrame, original_sales):


    stanControlDict = {
        'N': len(feature_df),
        'K1': len(controlFrame.columns), 
        'X1': np.array(controlFrame),
        'y': np.array(original_sales/original_sales.mean()),
        'max_intercept': min(original_sales/original_sales.mean())
    }



    return stanControlDict