#definition of hill function containing:
# - S = Shape
# - H = Half saturation point
# Must be applied for each point in time individually

import numpy as np



def hill_function(adstocked_spending, S, H):
    hill = []

    for spending in adstocked_spending:


        # print(spending)
        # print((1+spending/K))
        # print((1+spending/K)**-S)
        
        # hill_transformed_data = 1/(1+(spending/K)**-S)
        hill_transformed_data = (spending**S)/((H**S)+(spending**S))
        # print(hill_transformed_data)
        hill.append(hill_transformed_data)

    return hill

