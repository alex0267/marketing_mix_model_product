import Business_Output.applyParameters
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class ResponseCurve:

    def __init__(self, responseModel,responseCurveConfig,original_prediction, window=48, start=0):
        
        #initial response Model
        self.responseModel = responseModel
        self.responseCurveConfig = responseCurveConfig
        self.original_prediction = original_prediction
        self.original_spendings = None
        self.window = window
        self.start = start-1


        #changed data
        self.spendingsF = None

        #created metrices
        self.ROAS = None

        #generated ResponseCurve data
        self.spendings = {}
        self.prediction = {}
        self.volumeUplift = {}
        self.noSpendSimulation = 0

        #generated contribution data
        self.volumeContribution = {}

    def changeSpendings(self, touchpoint, lift):

        #select to be changed window
        originalSpendingsInWindow = self.responseModel.spendingsFrame[touchpoint].loc[self.start: self.start+self.window]
        # print('window')
        # print(originalSpendingsInWindow)
        #save original spendings as metric
        self.original_spendings = originalSpendingsInWindow.sum()
        #apply change
        changedSpendings = originalSpendingsInWindow*lift
                
        #change entire dataframe according to change
        spendings = self.responseModel.spendingsFrame.copy()
        spendings[touchpoint].loc[changedSpendings.index] = changedSpendings[:]

        return spendings, changedSpendings.sum()
        
    def simulateSales(self, spendings):
        # plt.plot(spendings)
        # plt.savefig('test.png')
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

    # def plotPredictions(self, lift):
    #     plt.plot(self.original_prediction, color='orange')
    #     plt.plot(self.prediction[lift], color='green')
    #     plt.savefig('plots/predictionComp.png')


    '''NOT AT RIGHT PLACE - NEEDS TO GO TO DECOMPOSE_CONTRIBUTION'''
    def generateVolumeContribution(self, touchpoint):

        noSpendSimulation = self.prediction[0.0][self.responseModel.responseModelConfig['max_lag']-self.start: self.start + self.window]
        currentSpendSimulation = self.prediction[1.0][self.responseModel.responseModelConfig['max_lag']-self.start: self.start + self.window]
        
        self.volumeContribution[touchpoint] = sum(currentSpendSimulation - noSpendSimulation)/ sum(currentSpendSimulation)

        return 0
    
    def generateResponseCurve(self, touchpoint):

        plt.plot(self.volumeUplift[touchpoint].keys(),self.volumeUplift[touchpoint].values())
        plt.savefig(f'plots/responseCurve_{touchpoint}.png')
        plt.clf()

    def calculateVolumeUplift(self, lift, prediction):
        
        if(self.start + self.window + self.responseModel.responseModelConfig['max_lag'] > len(self.responseModel.spendingsFrame)):
            prediction = prediction[self.start: self.start + self.window]
            print('prediction window does not contain post-change period since end of timeseries has been reached')
        #cut the prediction frame to only include change window + after-change window (incl. after effects)
        prediction = prediction[self.start: self.start + self.window + self.responseModel.responseModelConfig['max_lag']]

        #set the baseline simulation with no touchpoint expenses
        if(lift == 0.0):
            self.noSpendSimulation = prediction

        #Calculate the volume uplift as the difference between the current lift level and the no spend level
        #scope is the entire change & post-change period
        uplift = sum(prediction-self.noSpendSimulation)

        return uplift


    '''NOT IN USE - NEEDS REDEFINITION'''
    def calculateROAS(self):
        #calculate Return on Advertisements Spend by taking the difference as 
        #predicted sales - predicted sales simulated by spending nothing
        #and then comparing it to the spendings at the standard spending level

        self.ROAS = sum(self.original_prediction-self.prediction[0.0])/self.spendings[1.0]

    def run(self):
        
        #Generate curves for each touchpoint and lift level
        for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
            uplift = {}
            for lift in self.responseCurveConfig['SPEND_UPLIFT_TO_TEST']:

                #change spendings according to lift level and simulate the sales based on estimated parameters
                spendings, spendings_sum = self.changeSpendings(touchpoint = touchpoint, lift=lift)
                prediction = self.simulateSales(spendings)

                #extract a predictions for entire dataframe for each spending lift
                self.prediction[lift] = prediction

                #calculate the volumeUplift to generate the y-values of the response curve
                uplift[lift] = self.calculateVolumeUplift(lift, prediction)

            self.volumeUplift[touchpoint] = uplift

            self.generateResponseCurve(touchpoint)
            self.generateVolumeContribution(touchpoint)
        print('contributions')
        print(self.volumeContribution)
        print(sum(self.volumeContribution.values()))

