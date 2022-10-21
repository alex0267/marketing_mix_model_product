import BUSINESS_OUTPUT.applyParameters
import BUSINESS_OUTPUT.changeControlVariable
import TEST_SUITE.mainComparisonTests
import HELPER_FUNCTIONS.getIndex
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
        self.deltaBaseline={}

        #generate control variable influence
        self.deltaControlToNeutral={}

        #execute simulation of touchpoint lifts and calculate delta
        self.runTouchpointLift()

        #execute simulation of no touchpoint spendings to simulate the influence of the pure baseline
        self.runBaselineExtract()

        #execute simulation of neutral control level to simulate influence of control variables
        self.runControlExtract()

    def changeControl(self,controlVariable, subset):
        '''
        Define the neutral level per control variable and changed the control dataframe.
        Takes a single control variable or multiple in case of baseline simulation.
        '''

        #get indexes of data for respective time frame
        ind = HELPER_FUNCTIONS.getIndex.getIndex(indexColumns = self.responseModel.index_df,scope='YEAR' , subset=subset)


        #extract the control dataframe window that needs to be changed    
        originalControlWindow = self.responseModel.filteredFeature_df[self.responseModel.configurations['CONTROL_VARIABLES_BASE']][controlVariable].iloc[ind]

        #change control variable window to neutral position depending on control variable definition
        changedControl = BUSINESS_OUTPUT.changeControlVariable.changeControlVariable(originalControlWindow, controlVariable)

        #merge control variable window with the full window        
        zeroControl = pd.DataFrame(self.responseModel.filteredFeature_df[self.responseModel.configurations['CONTROL_VARIABLES_BASE']].copy())

        #if control variables are changed, each variable has to be changed individually
        if isinstance(controlVariable, list):
            for ctrl in controlVariable: 
                zeroControl[ctrl].loc[changedControl.index] = changedControl[ctrl]
        else:
            zeroControl[controlVariable].loc[changedControl.index] = changedControl[:]
        
        
        return zeroControl


    
    def changeSpendings(self, touchpoint, lift, subset):
        '''
        Take the scope (touchpoints to change), the change level(lift) and the timeframe (subset) as input variables for changing spendings
        The function returns a table that contains all touchpoint spendings with the changed spendings included
        (also works with multiple touchpoints (variable touchpoint is a list))
        '''

        #get indexes of data for respective time frame
        ind = HELPER_FUNCTIONS.getIndex.getIndex(indexColumns = self.responseModel.index_df,scope='YEAR' , subset=subset)
        


        originalSpendingsInWindow = self.responseModel.filteredFeature_df[self.responseModel.configurations['TOUCHPOINTS']][touchpoint].iloc[ind]


        #apply change
        changedSpendings = originalSpendingsInWindow*lift

        #change entire dataframe according to change
        spendings = self.responseModel.filteredFeature_df[self.responseModel.configurations['TOUCHPOINTS']].copy()
        
        #merge the changed section with the rest of the data

        #if multiple touchpoints are changed, each tp has to be changed individually
        if isinstance(touchpoint, list):
            for tp in touchpoint: 
                spendings[tp].loc[changedSpendings.index] = changedSpendings[tp]
        else:
            spendings[touchpoint].loc[changedSpendings.index] = changedSpendings[:]

        return spendings
        
    def simulateSales(self,subset=None, touchpoint=None, lift=None, spendings=None,control_df=None):
        '''take the changed spendings and simulate the sales based on the estimated parameters'''

        #use the existing control_df values if no changed are specified
        if spendings is None: spendings = self.responseModel.filteredFeature_df[self.responseModel.configurations['TOUCHPOINTS']].copy()
        if control_df is None: control_df = self.responseModel.filteredFeature_df[self.responseModel.configurations['CONTROL_VARIABLES_BASE']].copy()

        #extract sales predictions from changed spendingsFrame

        if(subset=='ALL' and touchpoint=='alex' and lift ==1.8):
            spendings.to_csv(f'TEST_SUITE/COMPARE_FRAMES/APPLY_COMPARISON/raw_data_{subset}_{touchpoint}_{lift}.csv')
            self.responseModel.feature_df[self.responseModel.configurations['TOUCHPOINTS']].to_csv(f'TEST_SUITE/COMPARE_FRAMES/APPLY_COMPARISON/original_spendings_{subset}_{touchpoint}_{lift}.csv')
            self.responseModel.filteredFeature_df[self.responseModel.configurations['SEASONALITY_VARIABLES_BASE']].to_csv(f'TEST_SUITE/COMPARE_FRAMES/APPLY_COMPARISON/seasonality_df_{subset}_{touchpoint}_{lift}.csv')
            control_df.to_csv(f'TEST_SUITE/COMPARE_FRAMES/APPLY_COMPARISON/control_df_{subset}_{touchpoint}_{lift}.csv')


        factor_df, y_pred = BUSINESS_OUTPUT.applyParameters.applyParametersToData(raw_data = spendings,
                                                            original_spendings = self.responseModel.feature_df[self.responseModel.configurations['TOUCHPOINTS']].copy(),
                                                            parameters = self.responseModel.parameters,
                                                            configurations= self.responseModel.configurations,
                                                            responseModelConfig = self.responseModel.responseModelConfig,
                                                            scope = self.responseModel.configurations['TOUCHPOINTS'],
                                                            seasonality_df = self.responseModel.filteredFeature_df[self.responseModel.configurations['SEASONALITY_VARIABLES_BASE']],
                                                            beta_seasonality= self.responseModel.beta_seasonality,
                                                            control_df = control_df,
                                                            beta_control = self.responseModel.beta_control)
        
        #prediction is equal to the (normalized prediction -1)*raw_sales.max()
        #we are taking the feature_df since the max value must be based on the entire dataset, not just the weeks applied
        prediction = (y_pred-1)*self.responseModel.feature_df['TARGET_VOL_SO'].max()
        print('TARGET')
        print(self.responseModel.feature_df['TARGET_VOL_SO'].max())
            
        return prediction

    def runTouchpointLift(self):
        '''
        Run the uplift simulation pipeline according to the configurations
        Scope : touchpoints
        '''

        #Execute calculation for different scopes (years individ. & all together)
        for subset in self.outputConfig['CHANGE_PERIODS']:
            #Simulate sales for each touchpoint and lift level
            for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                for lift in self.outputConfig['SPEND_UPLIFT_TO_TEST']:

                    #change spendings according to lift level and simulate the sales based on estimated parameters
                    spendings = self.changeSpendings(touchpoint = touchpoint, lift=lift, subset=subset)

                    #predict induced sales based on changed spendings with estimated parameters
                    prediction = self.simulateSales(subset, touchpoint, lift,spendings=spendings)

                    
                    #extract weekly changed spendings and predictions for each spending lift, touchpoint and subset combination
                    self.spendings[(subset,touchpoint,lift)] = spendings
                    self.prediction[(subset,touchpoint,lift)] = prediction

                    if(self.responseModel.configurations['SET_MASTER'] == True):
                        spendings.to_csv(f'TEST_SUITE/COMPARE_FRAMES/UPLIFT_COMPARISON/spendings_{subset}_{touchpoint}_{lift}.csv')
                        prediction.to_csv(f'TEST_SUITE/COMPARE_FRAMES/UPLIFT_COMPARISON/prediction{subset}_{touchpoint}_{lift}.csv')
                    else:
                        TEST_SUITE.mainComparisonTests.compareUplifts(spendings, prediction, subset, touchpoint,lift)


                #calculate the calculateDeltaCurrentToZero as the difference between uplift(1) and uplift(0)
                #for each touchpoint
                self.deltaCurrentToZero[(subset,touchpoint)] = self.prediction[(subset,touchpoint,1.0)]-self.prediction[(subset,touchpoint,0.0)]      

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
        controlVariable = [x for x in self.responseModel.configurations['CONTROL_VARIABLES_BASE']]
        for subset in self.outputConfig['CHANGE_PERIODS']:

            #simulate zero spendings to get baseline (ALL spendings and control variables)
            ZeroSpendings = self.changeSpendings(touchpoint = touchpoints, lift=0.0, subset=subset)
            ZeroControl = self.changeControl(controlVariable = controlVariable, subset = subset)
            ZeroSpendingsPredict = self.simulateSales(ZeroSpendings, ZeroControl)
            
            #simulate one spendings - could actually be replaced with a single lift=1 prediction for all (including RunTouchPointLift)
            #However, not foreseen in the current structure
            #CurrentSpendings = self.changeSpendings(touchpoint = touchpoints, lift=1.0, subset=subset)
            #CurrentSpendingsPredict = self.simulateSales(CurrentSpendings)
            #-> this part is not necessary since setting all to 0 already gives us the rest

            self.deltaBaseline[subset] = ZeroSpendingsPredict

    def runControlExtract(self):
        #Execute calculation for different scopes (years individ. & all together)
        for subset in self.outputConfig['CHANGE_PERIODS']:
            #Simulate sales for each touchpoint and lift level
            for control in self.responseModel.configurations['CONTROL_VARIABLES_BASE']:
                
                control_df = self.changeControl(controlVariable = [control], subset=subset)

                #predict induced sales based on changed control variable
                neutralPrediction = self.simulateSales(control_df=control_df)

                #predict the spendings with no changes to anything
                currentSpendingsPredict = self.simulateSales()


                #calculate the calculateDeltaControlToNeutral as the difference between the neutral control position and the current control position
                #for control variable
                self.deltaControlToNeutral[(subset,control)] =  currentSpendingsPredict - neutralPrediction
