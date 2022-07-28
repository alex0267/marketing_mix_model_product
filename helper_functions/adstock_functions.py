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

def adstock_transform(df, md_cols, adstock_params):
    '''
    params:
    df: original data
    md_cols: list, media variables to be transformed
    adstock_params: dict, 
        e.g., {'sem': {'L': 8, 'P': 0, 'D': 0.1}, 'dm': {'L': 4, 'P': 1, 'D': 0.7}}
    returns: 
    adstocked df
    '''
    md_df = pd.DataFrame()
    for md_col in md_cols:
        #L, P, D = adstock_params[md]['L'], adstock_params[md]['P'], adstock_params[md]['D']
        L, P, D = adstock_params[md_col]['L'], adstock_params[md_col]['P'], adstock_params[md_col]['D']

        xa = apply_adstock(df[md_col].values, L, P, D)
        md_df[md_col] = xa
    return md_df

#tp_2 = apply_adstock(data["touchpoint_2"], 4, 2, 0.9)
#tp_2 = apply_adstock(data["touchpoint"], 4, 4, 0.6)

#plt.plot(tp_2[:52], color='green')
#plt.plot(data["touchpoint_2"][:52], color='blue')