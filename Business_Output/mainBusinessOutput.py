import Business_Output.decompose_contribution
import Business_Output.UpliftSimulation
import Business_Output.ResponseCurves
import Business_Output.VolumeContribution
import Business_Output.extractSummary
import Business_Output.calculateROS
import Business_Output.calculateError
import Business_Output.plotContribution
import yaml

def createBusinessOutputs(responseModel, outputConfig, price_df):

    #Decompose absolute contribution by touchpoint
    #LEGACY
    #touchpointContribution_df, sales_prediction = Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, plot=True)
    
    #Simulate uplifts
    upliftSimulation = Business_Output.UpliftSimulation.UpliftSimulation(responseModel = responseModel,
                                                                       outputConfig = outputConfig) #define configurations for response Curve generation
  
    #Calculate volume contributions based on uplifts
    volumeContribution = Business_Output.VolumeContribution.VolumeContribution(upliftSimulation = upliftSimulation, 
                                                                                        responseModel = responseModel,
                                                                                        outputConfig = outputConfig)
    
    volumeContribution.calculateVolumeContribution()
    volumeContribution.correctContributionError()
    volumeContribution.calculateRelativeContribution()

    Business_Output.plotContribution.plotContribution(volumeContribution)

 

    #Generate response curves based on uplifts
    responseCurves = Business_Output.ResponseCurves.ResponseCurves(simulatedSpendings = upliftSimulation.spendings,
                                                                           simulatedSales = upliftSimulation.prediction, 
                                                                           responseModel = responseModel,
                                                                           outputConfig = outputConfig)

    #Calculate ROS based on volume contribution
    ROS = Business_Output.calculateROS.ROS_Calculation(responseModel = responseModel,
                                                       volumeContribution = volumeContribution,
                                                       outputConfig = outputConfig,
                                                       price_df = price_df)
    
    #Calculate error based on volume Contribution
    Business_Output.calculateError.calculateError(responseModel = responseModel,
                                   volumeContribution = volumeContribution)
    
    #Generate summary based on volumeContribution and ROS
    Business_Output.extractSummary.extractSummary(responseModel = responseModel,
                                                  volumeContribution = volumeContribution,
                                                  ROS_Calculation = ROS, 
                                                  outputConfig = outputConfig)
    
    return 0