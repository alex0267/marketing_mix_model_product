#definition of hill function containing:
# - S = Shape
# - H = Half saturation point
# Must be applied for each point in time individually

import numpy as np
import pandas as pd
import HELPER_FUNCTIONS.normalization
import math


def shape_function(adstocked_spendings,shape, scale, threshold, saturation):

  shaped_spendings=[]
  for spend in adstocked_spendings:

    if spend > threshold:
      #define scale ()

      scaled_form = (spend-threshold)/(scale)

      #high scaled_form-value leads to high shape value
      shaped = 1 - math.exp(-scaled_form**shape)
      shaped_spendings.append(shaped)

    else:
      shaped = 0
      shaped_spendings.append(shaped)


  return shaped_spendings


#Definition of Hill function (raw mathematical formulation)
#LEGACY
def hill_function_old(adstocked_spending, S, H):
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
        shape,scale = parameters[f'{touchpoint}_shape']['shape'], parameters[f'{touchpoint}_shape']['scale']
        threshold, saturation = responseModelConfig['SHAPE_THRESHOLD_VALUE'][touchpoint], responseModelConfig['SHAPE_SATURATION_VALUE'][touchpoint]
        threshold_normalized = HELPER_FUNCTIONS.normalization.normalize_value(threshold, raw_data[touchpoint], responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint], name = touchpoint)
        saturation_normalized = HELPER_FUNCTIONS.normalization.normalize_value(saturation, raw_data[touchpoint], responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint], name = touchpoint)
        

        #normalize data
        data_normalized, data_norm = HELPER_FUNCTIONS.normalization.normalize_feature(feature_df = data[touchpoint],
                                                                           norm_data = raw_data[touchpoint],
                                                                           normalization_steps = responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint], 
                                                                           responseModelConfig = responseModelConfig)

        #shape transformation of normalized data

        data_shaped = shape_function(data_normalized, 
                                     shape = shape,
                                     scale = scale,
                                     threshold = threshold_normalized,
                                     saturation = saturation_normalized)


        media_shaped[touchpoint] = data_shaped

    return media_shaped
