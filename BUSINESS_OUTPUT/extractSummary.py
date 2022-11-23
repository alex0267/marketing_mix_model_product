import pandas as pd
import numpy as np
#launch data extraction
def extractSummary(responseModel, volumeContribution,ROS_Calculation, outputConfig, name):
    '''
    Create a summary of all KPIs by week including
    - sales
    - spend
    - absolute & relative contribution
    - ROS
    '''
    resultSummary = pd.DataFrame()
    for brand in responseModel.configurations['BRANDS']:
        
        filteredFeature_df = responseModel.filteredFeature_df[responseModel.filteredFeature_df['BRAND']==brand].reset_index()
        

        responseModelInit_df = pd.DataFrame()

        for item in outputConfig['CONTRIBUTORS']:

            #iterate through touchpoints and add spendings and ROS (touchpoint specific information)
            if item in responseModel.configurations['TOUCHPOINTS']:
                spendings = filteredFeature_df[responseModel.configurations['TOUCHPOINTS']][item].rename('spendings')
                ROS = ROS_Calculation.ROS_Weekly[(brand,item)]
                ROS.replace([np.inf, -np.inf], 0, inplace=True)

            #iterate through control variables and fill the touchpoint specific cells with 0
            else:
                spendings = pd.Series([0 for x in range(len(filteredFeature_df['YEAR_WEEK']))]).rename('spendings')
                ROS = pd.Series([0 for x in range(len(filteredFeature_df['YEAR_WEEK']))])

            tp_df = pd.concat([filteredFeature_df['YEAR_WEEK'],filteredFeature_df['BRAND'],spendings,filteredFeature_df['TARGET_VOL_SO']], ignore_index=False, axis =1)
            tp_df['contributor'] = item
            tp_df['absolute_contribution'] = volumeContribution.deltaToZeroDict[(brand,'ALL')][item]
            tp_df['absolute_contribution_corrected'] = volumeContribution.absoluteContributionCorrected[(brand,'ALL')][item]
            tp_df['relative_contribution'] = volumeContribution.relativeContributions[(brand,'ALL')][item]
            tp_df['ROS'] = ROS

            responseModelInit_df = pd.concat([responseModelInit_df, tp_df], ignore_index=False,axis=0)
        
        #add ROS ratio
        responseModelInit_df['AVERAGE_PRICE'] = ROS_Calculation.prices_ALL[brand]
        responseModelInit_df = responseModelInit_df.sort_values(by=['YEAR_WEEK'])

        resultSummary = pd.concat([resultSummary,responseModelInit_df], axis=0)

       

    resultSummary.to_excel(f'OUTPUT/{name}/resultSummary_df.xlsx')
