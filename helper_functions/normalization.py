import numpy as np
import pandas as pd


def normalize(normalized_feature, norm_data, normalization_steps, configurations):

    #iterate through all normalization steps and change column based on parameters
    for step in normalization_steps:

        #application of custom normalization according to defined parameter (user-defined saturation per touchpoint)
        if step == 'custom_normalization':
            # scaling_factor = configurations.normalization_params_feature['brand_to_shape_params'][column_feature]['saturation']
            scaling_factor = 0
            normalized_feature = normalized_feature / scaling_factor


        #application of mean
        elif step == 'mean_across_brands':
            #define norming based on input
            scaling_factor = norm_data.mean()
 
            #avoid creating NAN's for columns with 0 spendings
            if(scaling_factor == 0):
                normalized_feature = normalized_feature
            else:
                normalized_feature = normalized_feature / scaling_factor
        
        #application of max-based normalization
        elif step == 'max_across_brands':
            #define norming based on input
            scaling_factor = norm_data.max()

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
        norm_data,
        normalization_steps,
        configurations
):
    '''
    The normalization process can be implemented for one or multiple columns
    In case the normalization is done via a variable norm e.g. max of touchpoint spendings the column that the norm will be based on must be passed
    The normalization steps refer to the order of execution of normalization
    The configurations are passed since reference to other parts of the responseModelConfig might be necesserary (MAKE OPTIONAL)
    '''
    print(norm_data)
    #define process if only one column is passed (pd.Series)
    if isinstance(feature_df, pd.Series):
        df = feature_df.copy()
        normalized_feature = normalize(df,norm_data, normalization_steps[df.name], configurations)

        return normalized_feature

    #define process if multiple columns are passed (pd.Series)
    elif isinstance(feature_df, pd.DataFrame):
        df = feature_df.copy()

        normalized_features = []

        for column in df:
            normalized_features.append(normalize(df[column],norm_data[column], normalization_steps[column], configurations))
        
        return pd.DataFrame(normalized_features).T


    