import Business_Output.decompose_contribution
import Business_Output.simulateResponseCurves

def createBusinessOutputs(responseModel, spendingsFrame):

    #Decompose contribution by touchpoint
    Business_Output.decompose_contribution.decompose_absolute_contribution(responseModel = responseModel, 
                                                                            spendingsFrame = spendingsFrame, plot=True)

    #Create response curves
    Business_Output.simulateResponseCurves.run(responseModel = responseModel,
                                                 spendingsFrame = spendingsFrame)

    return 0