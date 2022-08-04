import pandas as pd
import numpy as np

def apply_adstock(x, L, P, D):
    '''
    params:
    x: original media variable, array
    L: length
    P: peak, delay in effect
    D: decay, retain rate
    returns:
    array, adstocked media variable
    '''
    x = np.append(np.zeros(L - 1), x)

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

def adstock_transform(media, touchpoints, parameters):
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

        L, P, D = parameters[f'{touchpoint}_adstock']['L'], parameters[f'{touchpoint}_adstock']['P'], parameters[f'{touchpoint}_adstock']['D']

        adstocked = apply_adstock(media[touchpoint], L, P, D)
        media_adstocked[touchpoint] = adstocked
    return media_adstocked

#tp_2 = apply_adstock(data["touchpoint_2"], 4, 2, 0.9)
#tp_2 = apply_adstock(data["touchpoint"], 4, 4, 0.6)

#plt.plot(tp_2[:52], color='green')
#plt.plot(data["touchpoint_2"][:52], color='blue')