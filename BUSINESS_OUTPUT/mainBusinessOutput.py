import BUSINESS_OUTPUT.UpliftSimulation
import BUSINESS_OUTPUT.ResponseCurves
import BUSINESS_OUTPUT.VolumeContribution
import BUSINESS_OUTPUT.extractSummary
import BUSINESS_OUTPUT.ROSCalculation
import BUSINESS_OUTPUT.calculateError
import BUSINESS_OUTPUT.plotContribution

def createBusinessOutputs(responseModel, outputConfig, price_df):

    #Decompose absolute contribution by touchpoint
    
    #Simulate uplifts
    upliftSimulation = BUSINESS_OUTPUT.UpliftSimulation.UpliftSimulation(responseModel = responseModel,
                                                                        outputConfig = outputConfig) #define configurations for response Curve generation
    
    #Calculate volume contributions based on uplifts
    volumeContribution = BUSINESS_OUTPUT.VolumeContribution.VolumeContribution(upliftSimulation = upliftSimulation, 
                                                                                        responseModel = responseModel,
                                                                                        outputConfig = outputConfig)
    
    volumeContribution.calculateVolumeContribution()
    volumeContribution.correctContributionError()
    volumeContribution.calculateRelativeContribution()

    BUSINESS_OUTPUT.plotContribution.plotContribution(volumeContribution)


    #Generate response curves based on uplifts
    responseCurves = BUSINESS_OUTPUT.ResponseCurves.ResponseCurves(simulatedSpendings = upliftSimulation.spendings,
                                                                           simulatedSales = upliftSimulation.prediction, 
                                                                           responseModel = responseModel,
                                                                           outputConfig = outputConfig,
                                                                           price_df = price_df)

    #Calculate ROS based on volume contribution
    ROS = BUSINESS_OUTPUT.ROSCalculation.ROSCalculation(responseModel = responseModel,
                                                       volumeContribution = volumeContribution,
                                                       outputConfig = outputConfig,
                                                       price_df = price_df)
    
    #Calculate error based on volume Contribution
    BUSINESS_OUTPUT.calculateError.calculateError(responseModel = responseModel,
                                   volumeContribution = volumeContribution)
    
    #Generate summary based on volumeContribution and ROS
    BUSINESS_OUTPUT.extractSummary.extractSummary(responseModel = responseModel,
                                                  volumeContribution = volumeContribution,
                                                  ROS_Calculation = ROS, 
                                                  outputConfig = outputConfig)
    ''''''
    return 0