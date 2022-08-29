import helper_functions.adstock_functions
import helper_functions.transformations
import helper_functions.hill_function
import Business_Output.applyParameters
import numpy as np
import pandas as pd
import matplotlib
import sklearn.metrics
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
    plt.savefig('plots/estimatedContribution2.png')


def decompose_absolute_contribution(responseModel, plot = False):

    #apply parameters with responseModel
    factor_df, y_pred = Business_Output.applyParameters.applyParametersToData(raw_data = responseModel.spendingsFrame,
                                            original_spendings=responseModel.spendingsFrame, 
                                            parameters = responseModel.parameters,
                                            configurations = responseModel.configurations,
                                            responseModelConfig= responseModel.responseModelConfig,
                                            scope = responseModel.configurations['TOUCHPOINTS'],
                                            seasonality_df = responseModel.seasonality_df,
                                            seasonality_beta = responseModel.beta_seasonality)


    #getting max()+1 normalized sales variable 
    target = pd.DataFrame(np.exp(responseModel.stanDict['y'])).rename(columns={0:'sales'})

    factor_df['y_pred'], factor_df['y_true'] = y_pred, target

    # 3. calculate each media factor's contribution
    # media contribution = total volume – volume upon removal of the media factor
    mc_df = pd.DataFrame(columns=responseModel.configurations['TOUCHPOINTS']+['baseline'])
    for col in responseModel.configurations['TOUCHPOINTS']:
        mc_df[col] = factor_df['y_true'] - factor_df['y_true']/factor_df[col]
    mc_df['baseline'] = factor_df['baseline']
    mc_df['y_true'] = factor_df['y_true']

    # 4. scale contribution
    # predicted total media contribution: product of all media factors
    mc_df['mc_pred'] = mc_df[responseModel.configurations['TOUCHPOINTS']].apply(np.sum, axis=1)
    # true total media contribution: total volume - baseline
    mc_df['mc_true'] = mc_df['y_true'] - mc_df['baseline']


    # predicted total media contribution is slightly different from true total media contribution
    # scale each media factor’s contribution by removing the delta volume proportionally
    
    #DELTA - try with and without to see adaption effect
    mc_df['mc_delta'] =  mc_df['mc_pred'] - mc_df['mc_true']
    for col in responseModel.configurations['TOUCHPOINTS']:
        mc_df[col] = mc_df[col] - mc_df['mc_delta']*mc_df[col]/mc_df['mc_pred']

    # 5. scale mc_df based on original sales
    mc_df['sales'] = target
    for col in responseModel.configurations['TOUCHPOINTS']+['baseline']:
        mc_df[col] = mc_df[col]*mc_df['sales']/mc_df['y_true']
    
    # print('rmse (log-log model): ', 
    #      mean_squared_error(np.log(y_true), np.log(y_pred)) ** (1/2))
 
    compareFrame = target.merge(y_pred.rename('pred'), left_index=True, right_index=True)
    # compareFrame.to_csv("compare.csv")
    

    print('MAPE (multiplicative model): ', 
         helper_functions.transformations.mean_absolute_percentage_error(compareFrame['sales'], compareFrame['pred']))

    print('R2')
    print(sklearn.metrics.r2_score(compareFrame['sales'], compareFrame['pred']))

    #print("MAE")
    #print((sum(abs(compareFrame['sales']-compareFrame['pred'])))/len(compareFrame))


    #compare results on sales scale
    sales_prediction = (y_pred-1)*responseModel.target.max()
    # plt.plot((compareFrame['sales']-1)*responseModel.target.max(),  color='blue')
    # plt.plot(sales_prediction,  color='green')


    # if(plot == True):
    #     plotContribution(mc_df['mc_pred'],original_sales.max())
    # plt.plot(compareFrame['pred'],  color='red')
    #plt.plot(compareFrame['sales'])


    return mc_df, sales_prediction

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