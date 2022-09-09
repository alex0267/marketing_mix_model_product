import Business_Output.decompose_contribution
import Business_Output.simulateUplift
import Business_Output.generateResponseCurves
import Business_Output.calculateVolumeContribution
import Business_Output.extractSummary
import Business_Output.calculateRatios
import yaml

def createBusinessOutputs(responseModel, outputConfig):


    #Decompose absolute contribution by touchpoint
    touchpointContribution_df, sales_prediction = Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, plot=True)

    #Decompose relative contribution by touchpoint
    #mc_pct, mc_pct2 = Business_Output.decompose_contribution.calc_media_contrib_pct(touchpointContribution_df, media_vars=responseModel.configurations['TOUCHPOINTS'], period=52)
    
    #print(mc_pct)
    #print(mc_pct2)
    
    #Create response curves
    upliftSimulation = Business_Output.simulateUplift.UpliftSimulation(responseModel = responseModel,
                                                 outputConfig = outputConfig, #define configurations for response Curve generation
                                                 original_prediction = sales_prediction,
                                                 window = 48, #define length of change period
                                                 start=1) #define start week of change period (1 = first week) 
    
    volumeContribution = Business_Output.calculateVolumeContribution.VolumeContribution(upliftSimulation = upliftSimulation, 
                                                                                        responseModel = responseModel,
                                                                                        outputConfig = outputConfig)
    
    volumeContribution.calculateVolumeContribution()
    volumeContribution.correctContributionError()
    volumeContribution.calculateRelativeContribution()

    ratios = Business_Output.calculateRatios.RatioCalculation(responseModel = responseModel,
                                                                       volumeContribution = volumeContribution,
                                                                       outputConfig = outputConfig)
    ratios.calculateROS()

    Business_Output.extractSummary.extractSummary(responseModel = responseModel,
                                                  volumeContribution = volumeContribution,
                                                  ratios = ratios, 
                                                  outputConfig = outputConfig)
    
    return 0