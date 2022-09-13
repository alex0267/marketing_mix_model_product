import Business_Output.decompose_contribution
import Business_Output.simulateUplift
import Business_Output.generateResponseCurves
import Business_Output.calculateVolumeContribution
import Business_Output.extractSummary
import Business_Output.calculateROS
import yaml

def createBusinessOutputs(responseModel, outputConfig):

    #Decompose absolute contribution by touchpoint
    #LEGACY
    touchpointContribution_df, sales_prediction = Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, plot=True)
    
    #Simulate uplifts
    upliftSimulation = Business_Output.simulateUplift.UpliftSimulation(responseModel = responseModel,
                                                 outputConfig = outputConfig) #define configurations for response Curve generation
  
    #Calculate volume contributions based on uplifts
    volumeContribution = Business_Output.calculateVolumeContribution.VolumeContribution(upliftSimulation = upliftSimulation, 
                                                                                        responseModel = responseModel,
                                                                                        outputConfig = outputConfig)
    
    volumeContribution.calculateVolumeContribution()
    volumeContribution.correctContributionError()
    volumeContribution.calculateRelativeContribution()

    #Generate response curves based on uplifts
    responseCurves = Business_Output.generateResponseCurves.ResponseCurves(simulatedSpendings = upliftSimulation.spendings,
                                                                           simulatedSales = upliftSimulation.prediction, 
                                                                           responseModel = responseModel,
                                                                           outputConfig = outputConfig)

    #Calculate ROS based on volume contribution
    ROS = Business_Output.calculateROS.ROS_Calculation(responseModel = responseModel,
                                                       volumeContribution = volumeContribution,
                                                       outputConfig = outputConfig)
    
    #Generate summary based on volumeContribution and ROS
    Business_Output.extractSummary.extractSummary(responseModel = responseModel,
                                                  volumeContribution = volumeContribution,
                                                  ROS_Calculation = ROS, 
                                                  outputConfig = outputConfig)
    
    return 0