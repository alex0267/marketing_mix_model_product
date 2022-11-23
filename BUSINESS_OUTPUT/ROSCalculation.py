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
    def __init__(self, responseModel, volumeContribution, outputConfig, price_df, name):

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

        self.name = name

        #implement calculation
        self.runROSCalculation()

        

    def calculateROS(self,brand,index_df, filteredFeature_df):

        price_df = self.price_df[self.price_df['BRAND']==brand]['NET_PRICE'].reset_index()
        ROS_df = []

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

                for touchpoint in self.responseModel.baseConfig['TOUCHPOINTS']:
                    
                    totalVolumeContribution = (self.volumeContribution.absoluteContributionCorrected[(brand,scope)][touchpoint].iloc[ind])
                                    
                    prices = price_df['NET_PRICE'].iloc[ind]
                    
                    valueContribution = prices*totalVolumeContribution.values

                    totalSpendings = filteredFeature_df[self.responseModel.baseConfig['TOUCHPOINTS']][touchpoint].iloc[ind].reset_index(drop = True)

                    if (subset=='ALL' and scope == 'ALL'):
                        self.prices_ALL[brand] = prices
                        self.ROS_Weekly[(brand,touchpoint)] = valueContribution/totalSpendings

                    ratio = (valueContribution.sum()/totalSpendings.sum())
                    
                    ROS_df.append([brand,subset,scope, touchpoint,ratio])

                    self.ROS[(brand,subset,scope, touchpoint)] = ratio

        return ROS_df

    def runROSCalculation(self):
        ROS_df = []
        for brand in self.responseModel.baseConfig['BRANDS']:
            index_df = self.responseModel.index_df[self.responseModel.index_df['BRAND']==brand].reset_index()
            filteredFeature_df = self.responseModel.filteredFeature_df[self.responseModel.filteredFeature_df['BRAND']==brand].reset_index()
            ROS_df.append(self.calculateROS(brand,index_df,filteredFeature_df))


        ROS_df = [j for i in ROS_df for j in i]
        ROS_df = pd.DataFrame(ROS_df).rename(columns={0:'brand',1:'subset',2:'scope',3:'touchpoint',4:'ROS'})
        ROS_df.to_excel(f'OUTPUT/{self.name}/ROS_df.xlsx')
        return 0
