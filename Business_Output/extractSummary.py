import pandas as pd
import numpy as np
#launch data extraction
def extractSummary(responseModel, volumeContribution,ROS_Calculation, outputConfig):
    '''
    Create a summary of all KPIs by week including
    - sales
    - spend
    - absolute & relative contribution
    - ROS
    '''

    responseModelInit_df = pd.DataFrame()

    for item in outputConfig['CONTRIBUTORS']:

        #iterate through touchpoints and add spendings and ROS (touchpoint specific information)
        if item in responseModel.configurations['TOUCHPOINTS']:
            spendings = responseModel.spendingsFrame[item].rename('spendings')
            ROS = ROS_Calculation.ROS_Weekly[item]
            ROS.replace([np.inf, -np.inf], 0, inplace=True)

        #iterate through control variables and fill the touchpoint specific cells with 0
        else:
            spendings = pd.Series([0 for x in range(len(responseModel.indexColumns['YEAR_WEEK']))]).rename('spendings')
            ROS = pd.Series([0 for x in range(len(responseModel.indexColumns['YEAR_WEEK']))])

        tp_df = pd.concat([responseModel.indexColumns['YEAR_WEEK'],spendings,responseModel.target], ignore_index=False, axis =1)
        tp_df['contributor'] = item
        tp_df['absolute_contribution'] = volumeContribution.absoluteContributionCorrected['ALL'][item]
        tp_df['relative_contribution'] = volumeContribution.relativeContributions['ALL'][item]
        #tp_df['price'] = ROS.prices_ALL
        tp_df['ROS'] = ROS



        #responseModelInit_df = responseModelInit_df.append(tp_df)
        responseModelInit_df = pd.concat([responseModelInit_df, tp_df], ignore_index=False,axis=0)
    
    #add ROS ratio
    responseModelInit_df = responseModelInit_df.merge(ROS_Calculation.prices_ALL[['YEAR_WEEK', 'AVERAGE_PRICE']], how='inner', on='YEAR_WEEK')
    # responseModelInit_df['ROS'] = responseModelInit_df['absolute_contribution']/responseModelInit_df['spendings']
    # responseModelInit_df.replace([np.inf, -np.inf], 0, inplace=True)
    # responseModelInit_df.fillna( 0, inplace=True)
    print(responseModelInit_df)

    responseModelInit_df.to_excel('output_df/resultSummary_df.xlsx')
    #print(responseModelInit_df)