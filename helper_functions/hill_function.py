#definition of hill function containing:
# - S = Shape
# - H = Half saturation point
# Must be applied for each point in time individually

import numpy as np
import pandas as pd
import helper_functions.normalization

#Definition of Hill function (raw mathematical formulation)
def hill_function(adstocked_spending, S, H):
    hill = []

    for spending in adstocked_spending:

        hill_transformed_data = (spending**S)/((H**S)+(spending**S))
        hill.append(hill_transformed_data)

    return hill



#Definition of conversion process from Adstocked_media to Shaped_media
#After estimation transformation
def hill_transform(data, raw_data, scope, parameters, responseModelConfig):

    media_shaped = pd.DataFrame()
    for i,touchpoint in enumerate(scope):

        #Return estimated parameters from dictionary
        S,H = parameters[f'{touchpoint}_shape']['S'], parameters[f'{touchpoint}_shape']['H']
        
        #normalize data & mutliply by 5 to get 0-5 range
        data_normalized = helper_functions.normalization.normalize_feature(feature_df = data[touchpoint],
                                                                           norm_data = raw_data[touchpoint],
                                                                           normalization_steps = responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'], 
                                                                           configurations = responseModelConfig)


        # data_normalized = data[touchpoint]/raw_data[touchpoint].max()
        data_scaled = data_normalized*5
            
        #hill transformation of normalized data
        data_shaped = hill_function(data_scaled, S,H)

        #calculating the coefficient of y/x of the respective hill transformation
        #we double the normalized data since:
        #-> y = x*5 on a 0-10 range (definition limit for H of Shape function - user defined) 
        #-> Therefore, all x mappings are only half the size 
        #-> coefficient_of_growth = y/x*2
        coefficient = (data_shaped/data_normalized)

        #scale the adstocked information according to the hill transformation
        touchpoint_shaped = coefficient*data[touchpoint]


        media_shaped[touchpoint] = touchpoint_shaped

    return media_shaped
