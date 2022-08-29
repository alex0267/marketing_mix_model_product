import Business_Output.applyParameters
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class ResponseCurve:

    def __init__(self, responseModel,configurations,original_prediction, window=48, start=0, lift=1):
        
        #initial response Model
        self.responseModel = responseModel
        self.configurations = configurations
        self.original_prediction = original_prediction
        self.original_spendings = None
        self.window = window
        self.start = start-1
        self.lift = lift


        #changed data
        self.spendingsF = None

        #created metrices
        self.ROAS = None

        #generated ResponseCurve data
        self.spendings = {}
        self.prediction = {}
        self.volumeContribution = {}
        self.upliftContribution = {}


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
        
        #cut the prediction frame to only include change window + after-change window (incl. after effects)
        prediction = prediction[self.start: self.start + self.window + self.responseModel.responseModelConfig['max_lag']]
        
        return prediction

    def plotPredictions(self, lift):
        plt.plot(self.original_prediction, color='orange')
        plt.plot(self.prediction[lift], color='green')
        plt.savefig('plots/predictionComp.png')

    def plotResponseCurve(self, touchpoint):
        
        # plt.plot(self.volumeContribution.keys(),self.volumeContribution.values())
        # plt.savefig(f'plots/responseCurve_{touchpoint}_volume_Contribution.png')
        # plt.clf()

        plt.plot(self.upliftContribution.keys(),self.upliftContribution.values())
        plt.savefig(f'plots/responseCurve_{touchpoint}_uplift_Contribution.png')
        plt.clf()


    def calculateLift(self, prediction, spendings_sum):

        #calculate response curve based on 0 spendings prediction
        #might be subject to two errors but shows direct impact of touchpoint spendings
        volumeContribution = sum(prediction[1.0] - self.prediction[0.0])

        upliftContribution = sum(prediction-self.prediction[0.0])
        

        return volumeContribution,upliftContribution

    def calculateROAS(self):
        #calculate Return on Advertisements Spend by taking the difference as 
        #predicted sales - predicted sales simulated by spending nothing
        #and then comparing it to the spendings at the standard spending level

        self.ROAS = sum(self.original_prediction-self.prediction[0.0])/self.spendings[1.0]

    def run(self, plot):

        # for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:

        for lift in self.configurations['SPEND_UPLIFT_TO_TEST']:
            spendings, spendings_sum = self.changeSpendings(touchpoint = 'touchpoint_5', lift=lift)
            prediction = self.simulateSales(spendings)

            
            # print(prediction.sum())
            # print(spendings_sum)


            self.spendings[lift] = spendings_sum
            self.prediction[lift] = prediction
            self.volumeContribution[lift],self.upliftContribution[lift]  = self.calculateLift(prediction, spendings_sum)

            # print('sum')
            # print(spendings_sum)
            # print('pred')
            # print(prediction)
            # print('lift')
            # print(self.lift[lift])

            #self.calculateROAS()
            if (plot==True):
                self.plotResponseCurve('touchpoint_5')
                #self.plotPredictions(0.0)
            #pd.DataFrame([self.lift]).to_excel('tp3.xlsx')
        print('total')
        print(sum(self.prediction[1.0]-self.prediction[0.0])/sum(self.prediction[1.0]))

        


        

