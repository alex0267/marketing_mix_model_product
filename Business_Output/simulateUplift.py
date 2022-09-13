import Business_Output.applyParameters
import helper_functions.getIndex
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class UpliftSimulation:
    '''
    Simulation space to apply the estimated parameters to the changed spending matrix.

    Parameters:
    - responseModel: Class init
    - Uplift simulation prediction window size
    - Uplift simulation start

    Attributes:
    - spendings: Collection of changed spendings table for each scope
    - prediction: Collection of the generated lift predictions for each scope
    - DeltaCurrentToZero: Calculated difference between lift(1) and lift(0)
    - deltaBaseline: Influence of baseline sales deduced from touchpoint influence for each scope

    '''

    def __init__(self, responseModel,outputConfig):
        
        #initial response Model
        self.responseModel = responseModel
        self.outputConfig = outputConfig

        #generated Lift data
        self.spendings = {}
        self.prediction = {}
        self.deltaCurrentToZero = {}

        #generate baselineInfluence
        self.deltaBaseline=[]

        #execute simulation of touchpoint lifts and calculate delta
        self.runTouchpointLift()

        #execute simulation of no touchpoint spendings to simulate the influence of the pure baseline
        self.runBaselineExtract()

    def changeSpendings(self, touchpoint, lift, subset):
        '''
        Take the scope (touchpoints to change), the change level(lift) and the timeframe (subset) as input variables for changing spendings
        The function returns a table that contains all touchpoint spendings with the changed spendings included
        (also works with multiple touchpoints (variable touchpoint is a list))
        '''

        #get indexes of data for respective time frame
        ind = helper_functions.getIndex.getIndex(indexColumns = self.responseModel.indexColumns,scope='YEAR' , subset=subset)
        
        #select spendings from window
        # if isinstance(touchpoint, list):
        #     for x in 
        #     originalSpendingsInWindow = self.responseModel.spendingsFrame[touchpoint].iloc[ind]

        originalSpendingsInWindow = self.responseModel.spendingsFrame[touchpoint].iloc[ind]


        #apply change
        changedSpendings = originalSpendingsInWindow*lift

        #change entire dataframe according to change
        spendings = self.responseModel.spendingsFrame.copy()
        
        #merge the changed section with the rest of the data

        #if multiple touchpoints are changed, each tp has to be changed individually
        if isinstance(touchpoint, list):
            for tp in touchpoint: 
                spendings[tp].loc[changedSpendings.index] = changedSpendings[tp]
        else:
            spendings[touchpoint].loc[changedSpendings.index] = changedSpendings[:]

        return spendings
        
    def simulateSales(self, spendings):
        '''take the changed spendings and simulate the sales based on the estimated parameters'''

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

    def runTouchpointLift(self):
        '''
        Run the uplift simulation pipeline according to the configurations
        Scope : touchpoints
        '''

        summary = pd.DataFrame()
        #Execute calculation for different scopes (years individ. & all together)
        for subset in self.outputConfig['CHANGE_PERIODS']:
            #Simulate sales for each touchpoint and lift level
            for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                for lift in self.outputConfig['SPEND_UPLIFT_TO_TEST']:

                    #change spendings according to lift level and simulate the sales based on estimated parameters
                    spendings = self.changeSpendings(touchpoint = touchpoint, lift=lift, subset=subset)

                    #predict induced sales based on changed spendings with estimated parameters
                    prediction = self.simulateSales(spendings)

                    #extract summary for checking correctness of approach
                    if (touchpoint == 'touchpoint_5'):
                        summary = pd.concat([summary,spendings['touchpoint_5'].rename(f'tp_5_{lift}_{subset}'),spendings['touchpoint_6'].rename(f'tp_6'),prediction], axis=1)


                    #extract weekly changed spendings and predictions for each spending lift, touchpoint and subset combination
                    self.spendings[(subset,touchpoint,lift)] = spendings
                    self.prediction[(subset,touchpoint,lift)] = prediction

                    

                #calculate the calculateDeltaCurrentToZero as the difference between uplift(1) and uplift(0)
                #for each touchpoint
                self.deltaCurrentToZero[(subset,touchpoint)] = self.prediction[(subset,touchpoint,1.0)]-self.prediction[(subset,touchpoint,0.0)]

                summary.to_excel('summary.xlsx')
        #pd.DataFrame(self.prediction[('2021', 'touchpoint_5', 0.6)]).to_excel('predict.xlsx')

        
            

    def runBaselineExtract(self):
        '''
        Run the uplift simulation pipeline according to the configurations
        The target is to extract the baseline by simulating all touchpoints spendings to 0
        the control variables outside baseline are simulated on their relative neutral level which is not necessarily 0
        '''
        
        #merge all touchpoints (all influencers that have to be ommited from the baseline)
        #should include also the control variables such as promotion, distribution, ...
        #seasonality however stays part of the baseline
        touchpoints = [x for x in self.responseModel.configurations['TOUCHPOINTS']]
        for subset in self.outputConfig['CHANGE_PERIODS']:

            #simulate zero spendings to get baseline
            ZeroSpendings= self.changeSpendings(touchpoint = touchpoints, lift=0.0, subset=subset)
            ZeroSpendingsPredict = self.simulateSales(ZeroSpendings)
            

            #simulate one spendings - could actually be replaced with a single lift=1 prediction for all (including RunTouchPointLift)
            #However, not foreseen in the current structure
            CurrentSpendings = self.changeSpendings(touchpoint = touchpoints, lift=1.0, subset=subset)
            CurrentSpendingsPredict = self.simulateSales(CurrentSpendings)

            self.deltaBaseline = ZeroSpendingsPredict

        # print('baseline')
        # print(self.deltaBaseline)

        

        # print('spendings')
        # print(self.spendings)
        # print('prediction')
        # print(self.prediction)
        # print('delta')
        # print(self.deltaCurrentToZero)


