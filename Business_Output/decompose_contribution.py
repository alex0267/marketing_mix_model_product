import helper_functions.adstock_functions
import helper_functions.transformations
import helper_functions.hill_function
import Business_Output.applyParameters
import numpy as np
import pandas as pd
import matplotlib
import sklearn.metrics
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
    
    print('MAPE (multiplicative model): ', 
         helper_functions.transformations.mean_absolute_percentage_error(factor_df['y_true'], factor_df['y_pred']))

    print('R2')
    print(sklearn.metrics.r2_score(factor_df['y_true'], factor_df['y_pred']))

    #compare results on sales scale
    sales_prediction = (factor_df['y_pred']-1)*responseModel.target.max()
    plt.savefig('plots/prediction.png')
    plt.clf()

    return touchpointContribution_df, sales_prediction

'''NOT IN SCOPE ANYMORE'''
# calculate media contribution percentage
def calc_media_contrib_pct(touchpointContribution_df, media_vars, sales_col='sales', period=52):
    print('mc')
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