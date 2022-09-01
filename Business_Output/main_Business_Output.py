import Business_Output.decompose_contribution
import Business_Output.simulateResponseCurves
import yaml

def createBusinessOutputs(responseModel, responseCurveConfig):


    #Decompose absolute contribution by touchpoint
    touchpointContribution_df, sales_prediction = Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, plot=True)

    #Decompose relative contribution by touchpoint
    #mc_pct, mc_pct2 = Business_Output.decompose_contribution.calc_media_contrib_pct(touchpointContribution_df, media_vars=responseModel.configurations['TOUCHPOINTS'], period=52)
    
    #print(mc_pct)
    #print(mc_pct2)
    
    #Create response curves
    responseCurve = Business_Output.simulateResponseCurves.ResponseCurve(responseModel = responseModel,
                                                 responseCurveConfig = responseCurveConfig, #define configurations for response Curve generation
                                                 original_prediction = sales_prediction,
                                                 window = 48, #define length of change period
                                                 start=1) #define start week of change period (1 = first week) 
    
    responseCurve.run()
    
    
    return 0