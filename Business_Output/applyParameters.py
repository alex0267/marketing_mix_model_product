import numpy as np
import pandas as pd
import helper_functions

#use the estimated parameters to combine with model to calculate sales prediction

def applyParametersToData(raw_data,original_spendings, parameters, configurations, scope, seasonality_df, seasonality_beta):


    media_adstocked = helper_functions.adstock_functions.adstock_transform(media = raw_data[scope],
                                                                         touchpoints = scope,
                                                                         parameters=parameters)

    #media_shaped = media_adstocked
    media_shaped = helper_functions.hill_function.hill_transform(data = media_adstocked,
                                                        raw_data = original_spendings,
                                                        scope=scope, 
                                                        parameters=parameters, 
                                                        configurations=configurations)

    # plt.plot(data['touchpoint_4_adstocked'], color='blue')
    # plt.plot(media_shaped['touchpoint_4'], color='green')
    # plt.plot(data['touchpoint_4_shaped'], color= 'orange')
    # plt.savefig('testfig.png')

    #Normalize adstocked media via max accross brands with  +1
    #(adstock(touchpoint_x, param = estimated_parameters_x))/mean + 1
    for touchpoint in scope:
        normalization_steps = configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint]
        media_shaped[touchpoint] = media_shaped[touchpoint]/original_spendings[touchpoint].max()
        media_shaped[touchpoint] = media_shaped[touchpoint] + 1

    X = media_shaped


    #calculation of x**Beta for the media variables and the control model variables (= basesales)
    #we take the media_impressions (mean transformed)^Beta_i
    #x_Beta_matrix = X.apply(lambda x: x[:responseModel.num_media]**responseModel.beta[:responseModel.num_media], axis=1)

    factor_df = pd.DataFrame(columns=scope+['intercept']+configurations['SEASONALITY_VARIABLES_BASE'])
   
    for touchpoint in scope:
        factor_df[touchpoint] = X[touchpoint] ** parameters[f'{touchpoint}_beta']
    
    factor_df['intercept'] = np.exp(parameters['tau'])
    

    # 2. calculate the product of all factors -> y_pred
    # baseline = intercept * control factor = e^tau * X[13]^beta[13]
    #y_pred = baseline*((touchpoint_4_shaped)^Beta)*e^(seasonality*Beta)
    y_pred = factor_df.apply(np.prod, axis=1)*np.exp(np.dot(seasonality_df,seasonality_beta))

    factor_df['baseline'] = factor_df[['intercept']].apply(np.prod, axis=1)
    

    return factor_df, y_pred
