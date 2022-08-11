import Business_Output.decompose_contribution
import Business_Output.simulateResponseCurves
import yaml

def createBusinessOutputs(responseModel, spendingsFrame):

    with open('config/responseCurveConfig.yaml', 'r') as file:
            configurations = yaml.safe_load(file)

    #Decompose contribution by touchpoint
    df, sales_prediction = Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, 
                                                                            spendingsFrame = spendingsFrame, plot=True)

    #Create response curves
    responseCurve = Business_Output.simulateResponseCurves.ResponseCurve(responseModel = responseModel,
                                                 configurations = configurations, #define configurations for response Curve generation
                                                 original_prediction = sales_prediction,
                                                 window = 48, #define length of change period
                                                 start=1, #define start week of change period (1 = first week)
                                                 lift = 0) #define up-or-down lift simulation (1 = parameter-tested spendings)
    
    responseCurve.run()

    return 0