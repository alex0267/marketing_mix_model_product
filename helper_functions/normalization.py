import numpy as np
import pandas as pd


def normalize(normalized_feature, normalization_steps, configurations):

    #iterate through all normalization steps and change column based on parameters
    for step in normalization_steps:

        #application of custom normalization according to defined parameter (user-defined saturation per touchpoint)
        if step == 'custom_normalization':
            # scaling_factor = configurations.normalization_params_feature['brand_to_shape_params'][column_feature]['saturation']
            scaling_factor = 0
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

            if(scaling_factor == 0):
                normalized_feature = normalized_feature
            else:
                normalized_feature = normalized_feature / scaling_factor


        #application of natural logarithm (ln(x)) to the series +1
        elif step == 'logp1':
            normalized_feature = np.log(normalized_feature + 1)

    return normalized_feature



def normalize_feature(
        feature_df,
        normalization_steps,
        configurations
):
    
    #define process if only one column is passed (pd.Series)
    if isinstance(feature_df, pd.Series):
        df = feature_df.copy()
        normalized_feature = normalize(df, normalization_steps[df.name], configurations)

        return normalized_feature

    #define process if multiple columns are passed (pd.Series)
    elif isinstance(feature_df, pd.DataFrame):
        df = feature_df.copy()

        normalized_features = []

        for column in df:
            normalized_features.append(normalize(df[column], normalization_steps[column], configurations))
        
        return pd.DataFrame(normalized_features).T


    