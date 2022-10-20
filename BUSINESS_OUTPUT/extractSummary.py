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
            spendings = responseModel.spendings_df[item].rename('spendings')
            ROS = ROS_Calculation.ROS_Weekly[item]
            ROS.replace([np.inf, -np.inf], 0, inplace=True)

        #iterate through control variables and fill the touchpoint specific cells with 0
        else:
            spendings = pd.Series([0 for x in range(len(responseModel.index_df['YEAR_WEEK']))]).rename('spendings')
            ROS = pd.Series([0 for x in range(len(responseModel.index_df['YEAR_WEEK']))])

        tp_df = pd.concat([responseModel.index_df['YEAR_WEEK'],spendings,responseModel.target], ignore_index=False, axis =1)
        tp_df['contributor'] = item
        tp_df['absolute_contribution'] = volumeContribution.deltaToZeroDict['ALL'][item]
        tp_df['absolute_contribution_corrected'] = volumeContribution.absoluteContributionCorrected['ALL'][item]
        tp_df['relative_contribution'] = volumeContribution.relativeContributions['ALL'][item]
        tp_df['ROS'] = ROS

        responseModelInit_df = pd.concat([responseModelInit_df, tp_df], ignore_index=False,axis=0)
    
    #add ROS ratio
    responseModelInit_df['AVERAGE_PRICE'] = ROS_Calculation.prices_ALL
    responseModelInit_df = responseModelInit_df.sort_values(by=['YEAR_WEEK'])

    print(responseModelInit_df)

    responseModelInit_df.to_excel('OUTPUT_DF/resultSummary_df.xlsx')
