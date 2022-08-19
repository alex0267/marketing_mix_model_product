import Business_Output.decompose_contribution
import Business_Output.simulateResponseCurves
import yaml

def createBusinessOutputs(responseModel, responseCurveConfig):


    #Decompose contribution by touchpoint
    df, sales_prediction = Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, plot=True)

    
    #Create response curves
    responseCurve = Business_Output.simulateResponseCurves.ResponseCurve(responseModel = responseModel,
                                                 configurations = responseCurveConfig, #define configurations for response Curve generation
                                                 original_prediction = sales_prediction,
                                                 window = 52, #define length of change period
                                                 start=1, #define start week of change period (1 = first week)
                                                 lift = 0) #define up-or-down lift simulation (1 = parameter-tested spendings) 
    
    responseCurve.run(plot = True, absolute = True)
    
    return 0