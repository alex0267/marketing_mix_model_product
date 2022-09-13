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
    factor_df['y_true'] = pd.DataFrame(np.exp(responseModel.stanDict['y'])).rename(columns={0:'sales'})

    factor_df['y_pred'] = y_pred

    print(factor_df)

    touchpointContribution_df = pd.DataFrame(columns=responseModel.configurations['TOUCHPOINTS']+['baseline'])
    '''
    # 3. calculate each media factor's contribution
    # media contribution = total volume – volume upon removal of the media factor
    touchpointContribution_df = pd.DataFrame(columns=responseModel.configurations['TOUCHPOINTS']+['baseline'])
    for col in responseModel.configurations['TOUCHPOINTS']:
        touchpointContribution_df[col] = factor_df['y_true'] - factor_df['y_true']/factor_df[col]
    touchpointContribution_df['baseline'] = factor_df['baseline']
    touchpointContribution_df['y_true'] = factor_df['y_true']

    # 4. scale contribution
    # predicted total media contribution: product of all media factors
    touchpointContribution_df['mc_pred'] = touchpointContribution_df[responseModel.configurations['TOUCHPOINTS']].apply(np.sum, axis=1)
    # true total media contribution: total volume - baseline
    touchpointContribution_df['mc_true'] = touchpointContribution_df['y_true'] - touchpointContribution_df['baseline']


    # predicted total media contribution is slightly different from true total media contribution
    # scale each media factor’s contribution by removing the delta volume proportionally
    
    #DELTA - try with and without to see adaption effect
    touchpointContribution_df['mc_delta'] =  touchpointContribution_df['mc_pred'] - touchpointContribution_df['mc_true']
    for col in responseModel.configurations['TOUCHPOINTS']:
        touchpointContribution_df[col] = touchpointContribution_df[col] - touchpointContribution_df['mc_delta']*touchpointContribution_df[col]/touchpointContribution_df['mc_pred']

    # 5. scale touchpointContribution_df based on original sales
    touchpointContribution_df['sales'] = factor_df['y_true']
    for col in responseModel.configurations['TOUCHPOINTS']+['baseline']:
        touchpointContribution_df[col] = touchpointContribution_df[col]*touchpointContribution_df['sales']/touchpointContribution_df['y_true']
    '''
    # print('rmse (log-log model): ', 
    #      mean_squared_error(np.log(y_true), np.log(y_pred)) ** (1/2))
 
    #compareFrame = factor_df['y_true'].merge(y_pred.rename('pred'), left_index=True, right_index=True)
    # compareFrame.to_csv("compare.csv")
    
    print('MAPE (multiplicative model): ', 
         helper_functions.transformations.mean_absolute_percentage_error(factor_df['y_true'], factor_df['y_pred']))

    print('R2')
    print(sklearn.metrics.r2_score(factor_df['y_true'], factor_df['y_pred']))

    #print("MAE")
    #print((sum(abs(compareFrame['sales']-compareFrame['pred'])))/len(compareFrame))

    #compare results on sales scale
    sales_prediction = (factor_df['y_pred']-1)*responseModel.target.max()
    # plt.plot((compareFrame['sales']-1)*responseModel.target.max(),  color='blue')
    #plt.plot(compareFrame['sales'],  color='green')
    #plt.plot(compareFrame['pred'], color='red')
    plt.savefig('plots/prediction.png')
    plt.clf()


    # if(plot == True):
    #     plotContribution(touchpointContribution_df['mc_pred'],original_sales.max())
    # plt.plot(compareFrame['pred'],  color='red')
    #plt.plot(compareFrame['sales'])

    return touchpointContribution_df, sales_prediction

'''NOT IN SCOPE ANYMORE'''
# calculate media contribution percentage
def calc_media_contrib_pct(touchpointContribution_df, media_vars, sales_col='sales', period=52):
    '''
    returns:
    mc_pct: percentage over total sales
    mc_pct2: percentage over incremental sales (sales contributed by media channels)
    '''
    print('mc')
    #print(touchpointContribution_df)
    mc_pct = {}
    mc_pct2 = {}
    s = 0


    if period is None:
        for col in (media_vars):
            mc_pct[col] = (touchpointContribution_df[col]/touchpointContribution_df[sales_col]).mean()
    else:
        for col in (media_vars):
            mc_pct[col] = (touchpointContribution_df[col]/touchpointContribution_df[sales_col])[-period:].mean()
    for m in media_vars:
        s += mc_pct[m]
    for m in media_vars:
        mc_pct2[m] = mc_pct[m]/s

    plt.pie(mc_pct2.values())
    plt.savefig('plots/VolumeContribution.png')

    return mc_pct, mc_pct2