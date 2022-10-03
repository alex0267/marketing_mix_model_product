import pandas as pd
import numpy as np
import math

def apply_adstock_to_impression_spendings(spends, L, d):
    '''
    Adstock function with Length and decay parameter.
    To be applied when spendings are distributed according to when the impression takes place.
    Input: parameters, spendings list
    Output: adstocked spendings
    '''

    #add zeros to beginning to account for padding
    num_spendings = len(spends)
    spends = np.append(np.zeros(L-1), spends)

    #define decay of weights as d^s array
    #we reverse the list since weights are applied to past [t,t+1, t+2] -> [t-2, t-1, t]
    weights = [math.pow(d,s) for s in range(L)]
    weights.reverse()

    adstocked=[]
    #go through all sales (column has been appended by the max_length parameter)
    #+1 to not get outside of bounds
    for t in range(num_spendings):
        
        #subset spendings frame acc. to scope
        spend_subset = spends[t:t+L]
        
        #multiply weights with spend_subset
        sum = (spend_subset*weights).sum()

        adstocked.append(sum)

    return adstocked

def apply_adstock_to_direct_spendings(x, L,P, D):
    '''
    Adstock function with Length, peak and decay parameter.
    To be applied when spendings are attributed to expenses (not impressions).
    Input: parameters, spendings list
    Output: adstocked spendings
    '''

    #add zeros to beginning
    x = np.append(np.zeros(L), x)

    weights = np.zeros(L)
    for l in range(L):
        weight = D ** ((l - P) ** 2)
        weights[L - 1 - l] = weight

    adstocked_x = []
    for i in range(L - 1, len(x)):
        x_array = x[i - L + 1:i + 1]
        xi = sum(x_array * weights) / sum(weights)
        adstocked_x.append(xi)
    adstocked_x = np.array(adstocked_x)
    return adstocked_x

def adstock_transform(media, touchpoints, parameters,responseModelConfig):
    '''
    params:
    media: original data
    touchpints: list, media variables to be transformed
    parameters: dict
    returns: 
    adstocked df
    '''
    media_adstocked = pd.DataFrame()
    for i,touchpoint in enumerate(touchpoints):
        
        #CASE: adstock spendings come from data with impressions-oriented spendings (distributed)
        if(responseModelConfig['ADSTOCK_FUNCTION_TYPE'][touchpoint] == 'impression_spendings'):
            L, D = parameters[f'{touchpoint}_adstock']['L'], parameters[f'{touchpoint}_adstock']['D']
            adstocked = apply_adstock_to_impression_spendings(media[touchpoint], L, D)

        #CASE: adstock spendings come from data with direct spendings
        elif(responseModelConfig['ADSTOCK_FUNCTION_TYPE'][touchpoint] == 'direct_spendings'):
            L,P, D = parameters[f'{touchpoint}_adstock']['L'], parameters[f'{touchpoint}_adstock']['P'],parameters[f'{touchpoint}_adstock']['D']
            adstocked = apply_adstock_to_direct_spendings(media[touchpoint], L,P, D)

        else:
            print('unknown adstock function type')

        media_adstocked[touchpoint] = adstocked
    return media_adstocked

