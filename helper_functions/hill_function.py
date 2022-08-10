#definition of hill function containing:
# - S = Shape
# - H = Half saturation point
# Must be applied for each point in time individually

import numpy as np
import pandas as pd
import Data_Preparation.normalization


#Definition of Hill function (raw mathematical formulation)
def hill_function(adstocked_spending, S, H):
    hill = []

    for spending in adstocked_spending:

        hill_transformed_data = (spending**S)/((H**S)+(spending**S))
        hill.append(hill_transformed_data)

    return hill



#Definition of conversion process from Adstocked_media to Shaped_media
#After estimation transformation
def hill_transform(data, scope, parameters, configurations):

    media_shaped = pd.DataFrame()
    for i,touchpoint in enumerate(scope):

        #Return estimated parameters from dictionary
        S,H = parameters[f'{touchpoint}_shape']['S'], parameters[f'{touchpoint}_shape']['H']
        
        #normalize data & mutliply by 5 to get 0-5 range
        data_normalized = Data_Preparation.normalization.normalize_feature(data[touchpoint] , configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint], configurations, touchpoint)
        data_scaled = data_normalized*5
        data_scaled.to_excel(f'{touchpoint}_scaled_est.xlsx')
            
        #hill transformation of normalized data
        data_shaped = hill_function(data_scaled, S,H)

        #calculating the coefficient of y/x of the respective hill transformation
        #we double the normalized data since:
        #-> y = x*5 on a 0-10 range (definition limit for H of Shape function - user defined) 
        #-> Therefore, all x mappings are only half the size 
        #-> coefficient_of_growth = y/x*2
        coefficient = ((data_shaped/data_normalized))

        #scale the adstocked information according to the hill transformation
        touchpoint_shaped = coefficient*data[touchpoint]

        print(data[touchpoint])
        print(touchpoint_shaped)
        touchpoint_shaped.to_excel(f'{touchpoint}_shaped_after.xlsx')
        

        media_shaped[touchpoint] = touchpoint_shaped

    return media_shaped
