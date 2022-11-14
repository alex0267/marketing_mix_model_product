import numpy as np
import pandas as pd
import HELPER_FUNCTIONS.getIndex

class ROSCalculation:
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
        self.prices_ALL = {}

        #implement calculation
        self.runROSCalculation()

    def calculateROS(self,brand,index_df, filteredFeature_df):

        price_df = self.price_df[self.price_df['BRAND']==brand]['NET_PRICE'].reset_index()

        #calculate ROS based on 'ALL'
        for subset in self.outputConfig['CHANGE_PERIODS']:
            #execute a ROS calculation for all subsets when scope is ALL

            if(subset == 'ALL'): scopes = self.outputConfig['CHANGE_PERIODS']
            #execute ROS calculation for only the respective subset if scope is not ALL
            else: scopes = [subset]

            for scope in scopes:

                #get indexes of data for respective time frame
                ind, cont = HELPER_FUNCTIONS.getIndex.getIndex(indexColumns = index_df,scope='YEAR' , subset=scope)
                if cont == True: continue

                for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                    
                    totalVolumeContribution = (self.volumeContribution.absoluteContributionCorrected[(brand,scope)][touchpoint].iloc[ind])
                                    
                    prices = price_df['NET_PRICE'].iloc[ind]
                    
                    valueContribution = prices*totalVolumeContribution.values

                    totalSpendings = filteredFeature_df[self.responseModel.configurations['TOUCHPOINTS']][touchpoint].iloc[ind].reset_index(drop = True)

                    if (subset=='ALL' and scope == 'ALL'):
                        self.prices_ALL[brand] = prices
                        self.ROS_Weekly[(brand,touchpoint)] = valueContribution/totalSpendings

                    ratio = (valueContribution.sum()/totalSpendings.sum())


                    self.ROS[(brand,subset,scope, touchpoint)] = ratio

    def runROSCalculation(self):
        for brand in self.responseModel.configurations['BRANDS']:
            index_df = self.responseModel.index_df[self.responseModel.index_df['BRAND']==brand].reset_index()
            filteredFeature_df = self.responseModel.filteredFeature_df[self.responseModel.filteredFeature_df['BRAND']==brand].reset_index()
            self.calculateROS(brand,index_df,filteredFeature_df)

        return 0
