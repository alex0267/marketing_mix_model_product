from pickle import NONE
import numpy as np
import pandas as pd
import yaml

#Define configurations to be used
with open('CONFIG/responseModelConfig.yaml', 'r') as file:
            responseModelConfig = yaml.safe_load(file)

def normalize(normalized_feature, norm_data, normalization_steps):

    #iterate through all normalization steps and change column based on parameters
    for step in normalization_steps:
        scaling_factor = 0
        
        #application of custom normalization according to defined parameter (user-defined saturation per touchpoint)
        if step == 'custom_normalization':
            scaling_factor = responseModelConfig['SHAPE_SATURATION_VALUE'][normalized_feature.name]
            #scaling_factor = 0
            normalized_feature = normalized_feature / scaling_factor

        elif step == 'mean_across_brands':
            #define norming based on input
            scaling_factor = norm_data.mean()
 
            #avoid creating NAN's for columns with 0 spendings
            if(scaling_factor == 0):
                normalized_feature = normalized_feature
            else:
                normalized_feature = normalized_feature / scaling_factor
        
        elif step == 'max_across_brands':
            #define norming based on input
            scaling_factor = norm_data.max()

            if(scaling_factor == 0):
                normalized_feature = normalized_feature
            else:
                normalized_feature = normalized_feature / scaling_factor
        
        elif step in ["minus_mean"]:
            scaling_factor = norm_data.mean()
            normalized_feature = normalized_feature - scaling_factor

        #application of natural logarithm (ln(x)) to the series +1
        elif step == 'logp1':

            normalized_feature = np.log(normalized_feature + 1)


    return normalized_feature, scaling_factor


def normalize_feature(
        feature_df,
        norm_data,
        normalization_steps,
        responseModelConfig = None
):
    '''
    returns: normalized_feature, scaling_factor (mean or max)
    The normalization process can be implemented for one or multiple columns
    In case the normalization is done via a variable norm e.g. max of touchpoint spendings the column that the norm will be based on must be passed
    The normalization steps refer to the order of execution of normalization
    The configurations are passed since reference to other parts of the responseModelConfig might be necesserary (MAKE OPTIONAL)
    '''
    #define process if only one column is passed (pd.Series)
    if isinstance(feature_df, pd.Series):
        df = feature_df.copy()


        normalized_feature, scaling_factor = normalize(df,norm_data, normalization_steps)

        return normalized_feature, scaling_factor

    #define process if multiple columns are passed (pd.Series)
    elif isinstance(feature_df, pd.DataFrame):
        df = feature_df.copy()

        normalized_features = []
        scaling_factors = []

        for column in df:

            normalized_feature, scaling_factor = normalize(df[column],norm_data[column], normalization_steps[column])
            normalized_features.append(normalized_feature)
            scaling_factors.append(scaling_factor)
        
        return pd.DataFrame(normalized_features).T, scaling_factors

#Define normalization step for a single value
def normalize_value(value, norm_data, normalization_steps,name):

    #iterate through all normalization steps and change column based on parameters
    for step in normalization_steps:

        if(step == 'max_across_brands'):
            scaling_factor = max(norm_data)
            return value/scaling_factor
                
        #application of custom normalization according to defined parameter (user-defined saturation per touchpoint)
        if step == 'custom_normalization':
            scaling_factor = responseModelConfig['SHAPE_SATURATION_VALUE'][name]
            #scaling_factor = 0
            return value / scaling_factor