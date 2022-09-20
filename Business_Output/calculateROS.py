import numpy as np
import pandas as pd
import helper_functions.getIndex

class ROS_Calculation:
    '''
    Calculation of ROS ratio on the basis of the calculated volume contribution of each touchpoint.

    Parameters:
    - responseModel: Response Model class initialization to get data-specific parameters and the configurations
    - volumeContribution: Volume Contribution class initialization to get the absolute volume contribution
    - outputConfig: The type of change periods that apply to the ratio calculations
    - responseModel base configurations: The touchpoints

    Attributes:
    - ROS: Calculation of Return of Sales on a yearly basis
    - ROS_weekly: Calculation of Return of Sales on a weekly basis


    '''
    def __init__(self, responseModel, volumeContribution, outputConfig, price_df):

        #class inits and configurations
        self.responseModel = responseModel
        self.volumeContribution = volumeContribution
        self.outputConfig = outputConfig

        #gather ROS calculations
        self.ROS = {}
        self.ROS_Weekly={}

        #get price dict
        self.price_df = price_df
        self.prices_ALL = None

        #implement calculation
        self.calculateROS()

    def calculateROS(self):


        #calculate ROS based on 'ALL'
        for subset in self.outputConfig['CHANGE_PERIODS']:
            #execute a ROS calculation for all subsets when scope is ALL

            if(subset == 'ALL'): scopes = self.outputConfig['CHANGE_PERIODS']
            #execute ROS calculation for only the respective subset if scope is not ALL
            else: scopes = [subset]

            for scope in scopes:

                #get indexes of data for respective time frame
                ind = helper_functions.getIndex.getIndex(indexColumns = self.responseModel.indexColumns,scope='YEAR' , subset=scope)

                for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                    
                    totalVolumeContribution = (self.volumeContribution.absoluteContributionCorrected[scope][touchpoint].iloc[ind])
                    
                    prices = self.price_df[self.price_df['BRAND']==self.responseModel.configurations['BRANDS'][0]].reset_index().iloc[ind]
                    averagePrice = prices['AVERAGE']
                    

                    valueContribution = averagePrice*totalVolumeContribution.values

                    totalSpendings = self.responseModel.spendingsFrame[touchpoint].iloc[ind].reset_index(drop = True)


                    if (subset=='ALL' and scope == 'ALL'):
                        self.prices_ALL = prices
                        self.ROS_Weekly[touchpoint] = valueContribution/totalSpendings

                    ratio = (valueContribution.sum()/totalSpendings.sum())
                    # ratio.replace([np.inf, -np.inf], 0, inplace=True)
                    # print(f'check_{touchpoint}_{scope}_{subset}')
                    # print(totalVolumeContribution)
                    # print(totalVolumeContribution.sum())
                    # print(totalSpendings)
                    # print(totalSpendings.sum())
                    # print(totalVolumeContribution/totalSpendings)

                    self.ROS[(subset,scope, touchpoint)] = ratio

            #     print('ROS')
            #     print(subset)
            #     print(touchpoint)
            #     print(self.ROS_ALL[subset])

            # (dataset,scope)

        print(self.ROS)
            #print(self.volumeContribution.absoluteContributionCorrected[subset].iloc[ind])
            #originalSpendingsInWindow = self.responseModel.spendingsFrame[touchpoint].iloc[ind]
