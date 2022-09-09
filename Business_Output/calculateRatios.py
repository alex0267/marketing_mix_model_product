from numpy import sort_complex
import helper_functions.getIndex

class RatioCalculation:
    def __init__(self, responseModel, volumeContribution, outputConfig):

        #class inits and configurations
        self.responseModel = responseModel
        self.volumeContribution = volumeContribution
        self.outputConfig = outputConfig

        #gather ROS calculations
        self.ROS = {}
        self.ROS_Weekly={}

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
                    totalSpendings = self.responseModel.spendingsFrame[touchpoint].iloc[ind]
                    if (subset=='ALL' and scope == 'ALL'):
                        self.ROS_Weekly[touchpoint] = totalVolumeContribution/totalSpendings

                    self.ROS[(subset,scope, touchpoint)] = (totalVolumeContribution/totalSpendings).sum()

            #     print('ROS')
            #     print(subset)
            #     print(touchpoint)
            #     print(self.ROS_ALL[subset])

            # (dataset,scope)

        print(self.ROS)
            #print(self.volumeContribution.absoluteContributionCorrected[subset].iloc[ind])
            #originalSpendingsInWindow = self.responseModel.spendingsFrame[touchpoint].iloc[ind]
