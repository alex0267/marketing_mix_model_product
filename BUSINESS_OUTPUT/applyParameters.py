import numpy as np
import pandas as pd
import HELPER_FUNCTIONS.normalization
import HELPER_FUNCTIONS.adstockFunctions
import HELPER_FUNCTIONS.hillFunction

#use the estimated parameters to combine with model to calculate sales prediction

def applyParametersToData(raw_data,original_spendings, parameters, configurations, responseModelConfig, scope, seasonality_df, control_df):


    media_adstocked = HELPER_FUNCTIONS.adstockFunctions.adstock_transform(media = raw_data[scope],
                                                                         touchpoints = scope,
                                                                         parameters=parameters,
                                                                         responseModelConfig = responseModelConfig)


    #media_shaped = media_adstocked
    media_shaped = HELPER_FUNCTIONS.hillFunction.hill_transform(data = media_adstocked,
                                                        raw_data = original_spendings,
                                                        scope=scope, 
                                                        parameters=parameters, 
                                                        responseModelConfig=responseModelConfig)

    
    for touchpoint in scope:
        
        media_shaped[touchpoint] = media_shaped[touchpoint] + 1


    #calculation of x**Beta for the media variables and the control model variables (= basesales)
    #we take the media_impressions (mean transformed)^Beta_i
    
    factor_df = pd.DataFrame(columns=scope+['intercept']+configurations['SEASONALITY_VARIABLES_BASE']+configurations['CONTROL_VARIABLES_BASE'])
   
    for touchpoint in scope:
        factor_df[touchpoint] = media_shaped[touchpoint] ** parameters[f'{touchpoint}_beta']
    
    factor_df['intercept'] = np.exp(parameters['intercept'])
    

    # 2. calculate the product of all factors -> y_pred
    # baseline = intercept * control factor = e^intercept * media_shaped[13]^beta[13]
    #y_pred = baseline*((touchpoint_4_shaped)^Beta)*e^(seasonality*Beta)

    y_pred = factor_df.apply(np.prod, axis=1)*np.exp(np.dot(seasonality_df,parameters['seasonality_beta']))*np.exp(np.dot(control_df,parameters['control_beta']))

    #for now only the intercept makes up the baseline
    factor_df['baseline'] = factor_df[['intercept']].apply(np.prod, axis=1)
    

    return factor_df, y_pred