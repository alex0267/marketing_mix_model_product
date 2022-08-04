import numpy as np
import pandas as pd

def normalize_feature(
        feature_df: pd.DataFrame,
        normalization_steps,
        normalization_params_feature,
        column_feature
) -> pd.Series:

    normalized_feature = feature_df[column_feature].copy()

    #iterate through all normalization steps and change column based on parameters
    for step in normalization_steps:

        #application of custom normalization according to defined parameter (user-defined saturation per touchpoint)
        if step == 'custom_normalization':
            scaling_factor = normalization_params_feature['brand_to_shape_params'][column_feature]['saturation']
            normalized_feature = normalized_feature / scaling_factor


        #application of mean
        elif step == 'mean_across_brands':
            scaling_factor = normalized_feature.mean()
            
            #avoid creating NAN's for columns with 0 spendings
            if(scaling_factor == 0):
                normalized_feature = normalized_feature
            else:
                normalized_feature = normalized_feature / scaling_factor
        
        #application of max-based normalization
        elif step == 'max_across_brands':
            scaling_factor = normalized_feature.max()
            normalized_feature = normalized_feature / scaling_factor


        #application of natural logarithm (ln(x)) to the series +1
        elif step == 'logp1':
            normalized_feature = np.log(normalized_feature + 1)



    return normalized_feature

