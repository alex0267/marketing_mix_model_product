import Business_Output.applyParameters
import helper_functions.getIndex
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class UpliftSimulation:

    def __init__(self, responseModel,responseCurveConfig,original_prediction, window=48, start=0):
        
        #initial response Model
        self.responseModel = responseModel
        self.responseCurveConfig = responseCurveConfig
        self.original_prediction = original_prediction
        self.original_spendings = None
        self.window = window
        self.start = start-1

        #generated ResponseCurve data
        self.spendings = {}
        self.prediction = {}
        self.deltaCurrentToZero = {}

        #execute pipeline
        self.run()

    def changeSpendings(self, touchpoint, lift, subset):

        #get indexes of data for respective time frame
        ind = helper_functions.getIndex.getIndex(indexColumns = self.responseModel.indexColumns,scope='YEAR' , index=subset)
        
        #select spendings from window
        originalSpendingsInWindow = self.responseModel.spendingsFrame[touchpoint].iloc[ind]

        #save original spendings as metric
        self.original_spendings = originalSpendingsInWindow.sum()

        #apply change
        changedSpendings = originalSpendingsInWindow*lift
                
        #change entire dataframe according to change
        spendings = self.responseModel.spendingsFrame.copy()
        spendings[touchpoint].loc[changedSpendings.index] = changedSpendings[:]

        return spendings
        
    def simulateSales(self, spendings):

        #extract sales predictions from changed spendingsFrame
        factor_df, y_pred = Business_Output.applyParameters.applyParametersToData(raw_data = spendings,
                                                            original_spendings = self.responseModel.spendingsFrame.copy(),
                                                            parameters = self.responseModel.parameters,
                                                            configurations= self.responseModel.configurations,
                                                            responseModelConfig = self.responseModel.responseModelConfig,
                                                            scope = self.responseModel.configurations['TOUCHPOINTS'],
                                                            seasonality_df = self.responseModel.seasonality_df,
                                                            seasonality_beta= self.responseModel.beta_seasonality)
        
        #prediction is equal to the (normalized prediction -1)*raw_sales.max()
        prediction = (y_pred-1)*self.responseModel.target.max()
            
        return prediction

    def run(self):
        
        #Execute calculation for different scopes (years individ. & all together)
        for subset in self.responseCurveConfig['CHANGE_PERIODS']:
            #Simulate sales for each touchpoint and lift level
            for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                for lift in self.responseCurveConfig['SPEND_UPLIFT_TO_TEST']:

                    #change spendings according to lift level and simulate the sales based on estimated parameters
                    spendings = self.changeSpendings(touchpoint = touchpoint, lift=lift, subset=subset)
                    prediction = self.simulateSales(spendings)

                    #extract weekly changed spendings and predictions for each spending lift and touchpoint
                    self.spendings[subset][touchpoint][lift] = spendings
                    self.prediction[subset][touchpoint][lift] = prediction

                #calculate the calculateDeltaCurrentToZero as the difference between uplift(1) and uplift(0)
                #for each touchpoint
                self.deltaCurrentToZero[subset][touchpoint] = self.prediction[1.0]-self.prediction[0.0]

        print('spendings')
        print(self.spendings)
        print('prediction')
        print(self.prediction)
        print('delta')
        print(self.deltaCurrentToZero)


