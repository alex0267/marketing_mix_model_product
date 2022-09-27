import numpy as np
import pandas as pd
import helper_functions.normalization

#use the estimated parameters to combine with model to calculate sales prediction

def applyParametersToData(raw_data,original_spendings, parameters, configurations, responseModelConfig, scope, seasonality_df, beta_seasonality, control_df, beta_control):


    media_adstocked = helper_functions.adstock_functions.adstock_transform(media = raw_data[scope],
                                                                         touchpoints = scope,
                                                                         parameters=parameters,
                                                                         responseModelConfig = responseModelConfig)


    #media_shaped = media_adstocked
    media_shaped = helper_functions.hill_function.hill_transform(data = media_adstocked,
                                                        raw_data = original_spendings,
                                                        scope=scope, 
                                                        parameters=parameters, 
                                                        responseModelConfig=responseModelConfig)

    # plt.plot(data['touchpoint_4_adstocked'], color='blue')
    # plt.plot(media_shaped['touchpoint_4'], color='green')
    # plt.plot(data['touchpoint_4_shaped'], color= 'orange')
    # plt.savefig('testfig.png')

    #Normalize adstocked media via max accross brands with  +1
    #(adstock(touchpoint_x, param = estimated_parameters_x))/mean + 1

    
    for touchpoint in scope:
        #media_shaped[touchpoint], data_norm = helper_functions.normalization.normalize_feature(media_shaped[touchpoint],media_shaped[touchpoint],responseModelConfig['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint])
        
        #media_shaped[touchpoint] = media_shaped[touchpoint]/original_spendings[touchpoint].max()
        media_shaped[touchpoint] = media_shaped[touchpoint] + 1


    #calculation of x**Beta for the media variables and the control model variables (= basesales)
    #we take the media_impressions (mean transformed)^Beta_i
    
    factor_df = pd.DataFrame(columns=scope+['intercept']+configurations['SEASONALITY_VARIABLES_BASE']+configurations['CONTROL_VARIABLES_BASE'])
   
    for touchpoint in scope:
        factor_df[touchpoint] = media_shaped[touchpoint] ** parameters[f'{touchpoint}_beta']
    
    factor_df['intercept'] = np.exp(parameters['tau'])
    

    # 2. calculate the product of all factors -> y_pred
    # baseline = intercept * control factor = e^tau * media_shaped[13]^beta[13]
    #y_pred = baseline*((touchpoint_4_shaped)^Beta)*e^(seasonality*Beta)
    # print(beta_control)
    # print(control_df)
    y_pred = factor_df.apply(np.prod, axis=1)*np.exp(np.dot(seasonality_df,beta_seasonality))*np.exp(np.dot(control_df,beta_control))

    #for now only the intercept makes up the baseline
    factor_df['baseline'] = factor_df[['intercept']].apply(np.prod, axis=1)
    

    return factor_df, y_pred