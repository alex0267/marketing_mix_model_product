import helper_functions.adstock_functions
import helper_functions.transformations
import helper_functions.hill_function
import Data_Preparation.normalization
import numpy as np
import pandas as pd
import matplotlib
# matplotlib.use("TkAgg")
#https://pyimagesearch.com/2015/08/24/resolved-matplotlib-figures-not-showing-up-or-displaying/

from matplotlib import pyplot as plt


# Decompose sales to media channels' contribution
# Each media channel's contribution = total sales - sales upon removal the channel    

def plotContribution(prediction, max_sales):
    
    data = pd.DataFrame(prediction*max_sales)
    plt.figure()
    plt.plot(data[:], color="black")
    plt.show(block=True)
    plt.savefig('estimatedContribution2.png')

def decompose_absolute_contribution(responseModel, feature_df, original_sales, data,plot = False):


    #Adstock media variables according to estimated parameters
    #adstock(touchpoint_x, param = estimated_parameters_x)
    media_adstocked = helper_functions.adstock_functions.adstock_transform(feature_df[responseModel.configurations['TOUCHPOINTS']], responseModel.configurations['TOUCHPOINTS'], responseModel.parameters)
    print('adstocked')
    print(media_adstocked)

    
    #media_shaped = media_adstocked
    media_shaped = helper_functions.hill_function.hill_transform(media_adstocked,responseModel)

    plt.plot(media_shaped['touchpoint_4'], color='green')
    plt.plot(data['touchpoint_4_shaped'], color= 'orange')
    plt.savefig('testfig.png')

    #Normalize adstocked media via max accross brands with  +1
    #(adstock(touchpoint_x, param = estimated_parameters_x))/mean + 1
    for touchpoint in responseModel.configurations['TOUCHPOINTS']:
        normalization_steps = responseModel.configurations['NORMALIZATION_STEPS_TOUCHPOINTS'][touchpoint]
        media_shaped[touchpoint] = Data_Preparation.normalization.normalize_feature(media_shaped, normalization_steps, responseModel.configurations, touchpoint)
        media_shaped[touchpoint] = media_shaped[touchpoint] + 1

    X = media_shaped

    #getting max()+1 normalized sales variable 
    target = pd.DataFrame(np.exp(responseModel.stanDict['y'])).rename(columns={0:'sales'})


    #calculation of x**Beta for the media variables and the control model variables (= basesales)
    #we take the media_impressions (mean transformed)^Beta_i
    #x_Beta_matrix = X.apply(lambda x: x[:responseModel.num_media]**responseModel.beta[:responseModel.num_media], axis=1)

    factor_df = pd.DataFrame(columns=responseModel.configurations['TOUCHPOINTS']+['intercept']+responseModel.configurations['SEASONALITY_VARIABLES_BASE'])
    for i in range(responseModel.num_media):
        colname = responseModel.configurations['TOUCHPOINTS'][i]
        factor_df[colname] = X[colname] ** responseModel.parameters[f'{colname}_beta']
 
    
    factor_df['intercept'] = np.exp(responseModel.parameters['tau'])

    
    # 2. calculate the product of all factors -> y_pred
    # baseline = intercept * control factor = e^tau * X[13]^beta[13]
    y_pred = factor_df.apply(np.prod, axis=1)*np.exp(np.dot(responseModel.seasonality_df,responseModel.beta_seasonality))
    factor_df['y_pred'], factor_df['y_true2'] = y_pred, target
    factor_df['baseline'] = factor_df[['intercept']].apply(np.prod, axis=1)


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

    #Delta was excluded from the calculation since it distorts the actual predictive power of the model
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
    # plt.plot(compareFrame['sales'],  color='blue')
    # plt.plot(compareFrame['pred'],  color='green')
    # print('comp')
    # print(compareFrame['sales'])
    # print(compareFrame['pred'])

    # if(plot == True):
    #     plotContribution(mc_df['mc_pred'],original_sales.max())
    # plt.plot(compareFrame['pred'],  color='red')
    #plt.plot(compareFrame['sales'])

    plt.savefig('sales2.png')

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