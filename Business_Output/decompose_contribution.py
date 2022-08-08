import helper_functions.adstock_functions
import helper_functions.transformations
import Data_Preparation.normalization
import numpy as np
import pandas as pd

import matplotlib
# matplotlib.use("TkAgg")
#https://pyimagesearch.com/2015/08/24/resolved-matplotlib-figures-not-showing-up-or-displaying/

from matplotlib import pyplot as plt


# Decompose sales to media channels' contribution
# Each media channel's contribution = total sales - sales upon removal the channel    

def plotContribution(prediction, mean_sales):
    
    data = pd.DataFrame(prediction*mean_sales)
    plt.figure()
    plt.plot(data[:], color="black")
    plt.show(block=True)
    plt.savefig('estimatedContribution.png')

def decompose_absolute_contribution(responseModel, feature_df, original_sales, plot = False):

    
    # sales_mean_logp1 = feature_df['sales']
    # seasonality_sales_mean_logp1 = sales_mean_logp1*(np.dot(responseModel.stanDict['seasonality'],(responseModel.beta_seasonality)))
    # seasonality_sales_mean_p1 = np.exp(seasonality_sales_mean_logp1)
    # seasonality_sales_mean = np.exp(seasonality_sales_mean_logp1)-1
    # seasonality_sales = seasonality_sales_mean*original_sales.mean()


    # original_sales = seasonality_sales
    # target = pd.DataFrame(seasonality_sales_mean_p1).rename(columns={0:'sales'})

    #print((np.dot(responseModel.stanDict['seasonality'],(responseModel.beta_seasonality)))*(original_sales/original_sales.mean()))

    #Adstock media variables according to estimated parameters
    #adstock(touchpoint_x, param = estimated_parameters_x)
    media_adstocked = helper_functions.adstock_functions.adstock_transform(feature_df[responseModel.configurations['TOUCHPOINTS']], responseModel.configurations['TOUCHPOINTS'], responseModel.parameters)

    #Normalize adstocked media via max accross brands with  +1
    #(adstock(touchpoint_x, param = estimated_parameters_x))/mean + 1
    for touchpoint in responseModel.configurations['TOUCHPOINTS']:
        normalization_steps = responseModel.configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint]
        media_adstocked[touchpoint] = Data_Preparation.normalization.normalize_feature(media_adstocked, normalization_steps, responseModel.configurations, touchpoint)
        media_adstocked[touchpoint] = media_adstocked[touchpoint] + 1

    X = media_adstocked



    #getting max()+1 normalized sales variable 
    target = pd.DataFrame(np.exp(responseModel.stanDict['y'])).rename(columns={0:'sales'})

    # print('target')
    # print(responseModel.stanDict['y'])

    #calculation of x**Beta for the media variables and the control model variables (= basesales)
    #we take the media_impressions (mean transformed)^Beta_i
    #x_Beta_matrix = X.apply(lambda x: x[:responseModel.num_media]**responseModel.beta[:responseModel.num_media], axis=1)

    factor_df = pd.DataFrame(columns=responseModel.configurations['TOUCHPOINTS']+['intercept']+responseModel.configurations['SEASONALITY_VARIABLES_BASE'])
    for i in range(responseModel.num_media):
        colname = responseModel.configurations['TOUCHPOINTS'][i]
        factor_df[colname] = X[colname] ** responseModel.parameters[f'{colname}_beta']
 

    #here the control model parameters come into play 
    #First attempt with assumption: log(y/u+1) = B*log(adstock/u+1) + (B*dummy_month) + tau (with u = mean)
    #Therefore we apply log(B*dummy_month)

    # for i in range(len(responseModel.configurations['SEASONALITY_VARIABLES_BASE'])):
    #     season = responseModel.configurations['SEASONALITY_VARIABLES_BASE'][i]
    #     factor_df[colname] = np.log(controlFrame[season] * responseModel.parameters[season])
    
    factor_df['intercept'] = np.exp(responseModel.parameters['tau'])

    # print('dot_here')
    # print(factor_df.apply(np.prod, axis=1))
    # print(np.dot(controlFrame,responseModel.beta_seasonality))
    # print(factor_df.apply(np.prod, axis=1)*np.dot(controlFrame,responseModel.beta_seasonality))
    
    # 2. calculate the product of all factors -> y_pred
    # baseline = intercept * control factor = e^tau * X[13]^beta[13]
    y_pred = factor_df.apply(np.prod, axis=1)*np.exp(np.dot(responseModel.seasonality_df,responseModel.beta_seasonality))
    factor_df['y_pred'], factor_df['y_true2'] = y_pred, target
    factor_df['baseline'] = factor_df[['intercept']].apply(np.prod, axis=1)

    # print('factors here')
    # print(factor_df)

    # 3. calculate each media factor's contribution
    # media contribution = total volume – volume upon removal of the media factor
    mc_df = pd.DataFrame(columns=responseModel.configurations['TOUCHPOINTS']+['baseline'])
    for col in responseModel.configurations['TOUCHPOINTS']:
        mc_df[col] = factor_df['y_true2'] - factor_df['y_true2']/factor_df[col]
    mc_df['baseline'] = factor_df['baseline']
    mc_df['y_true2'] = factor_df['y_true2']

    # 4. scale contribution
    # predicted total media contribution: product of all media factors
    mc_df['mc_pred'] = mc_df[responseModel.configurations['TOUCHPOINTS']].apply(np.sum, axis=1)
    # true total media contribution: total volume - baseline
    mc_df['mc_true'] = mc_df['y_true2'] - mc_df['baseline']
    # predicted total media contribution is slightly different from true total media contribution
    # scale each media factor’s contribution by removing the delta volume proportionally

    # mc_df['mc_delta'] =  mc_df['mc_pred'] - mc_df['mc_true']
    # for col in responseModel.configurations['TOUCHPOINTS']:
    #     mc_df[col] = mc_df[col] - mc_df['mc_delta']*mc_df[col]/mc_df['mc_pred']

    # 5. scale mc_df based on original sales
    mc_df['sales'] = target
    for col in responseModel.configurations['TOUCHPOINTS']+['baseline']:
        mc_df[col] = mc_df[col]*mc_df['sales']/mc_df['y_true2']
    
    # print('rmse (log-log model): ', 
    #      mean_squared_error(np.log(y_true2), np.log(y_pred)) ** (1/2))
 

    true = target
    pred = y_pred

    compareFrame = true.merge(pred.rename('pred'), left_index=True, right_index=True)
    compareFrame.to_csv("compare.csv")
    


    print('MAPE (multiplicative model): ', 
         helper_functions.transformations.mean_absolute_percentage_error(compareFrame['sales'], compareFrame['pred']))

    print("MAE")
    print((sum(abs(compareFrame['sales']-compareFrame['pred'])))/len(compareFrame))

    #Plot the error if wanted
    if(plot == True):
        plotContribution(mc_df['mc_pred'],original_sales.mean())
    plt.plot(compareFrame['pred'])
    plt.savefig('sales.png')

    return mc_df

# calculate media contribution percentage - NOT TESTED YET
def calc_media_contrib_pct(mc_df, media_vars, sales_col='sales', period=52):
    '''
    returns:
    mc_pct: percentage over total sales
    mc_pct2: percentage over incremental sales (sales contributed by media channels)
    '''
    mc_pct = {}
    mc_pct2 = {}
    s = 0
    if period is None:
        for col in (media_vars):
            mc_pct[col] = (mc_df[col]/mc_df[sales_col]).mean()
    else:
        for col in (media_vars):
            mc_pct[col] = (mc_df[col]/mc_df[sales_col])[-period:].mean()
    for m in media_vars:
        s += mc_pct[m]
    for m in media_vars:
        mc_pct2[m] = mc_pct[m]/s
    return mc_pct, mc_pct2