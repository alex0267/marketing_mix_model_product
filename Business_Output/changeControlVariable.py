import pandas as pd

def changeControlVariable(originalControlWindow, controlVariable):

    control_df = pd.DataFrame()
    for variable in controlVariable:

        if(variable == 'distribution'):
            #distribution: distribution is neutral if the minimum distribution is reached
            #formula = (distribution(t) - min(distribution)) / min(distribution)
            #therefore, if the minimum distribution applies to the entire dataset, the feature is 0 for all weeks

            #create series of 0 for each element in scope
            distribution_df = pd.Series([0 for x in range(len(originalControlWindow))]).rename('distribution')

            #merge with existing controlFrame
            control_df = pd.concat([control_df,distribution_df], axis=1)

        if(variable == 'covid'):
            #create series of 0 for each element in scope
            covid_df = pd.Series([0 for x in range(len(originalControlWindow))]).rename('covid')
            #merge with existing controlFrame
            control_df = pd.concat([control_df,covid_df], axis=1)


    return control_df