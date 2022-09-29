import pandas as pd


class VolumeContribution:
    '''
    Volume contribution calculation for the standard spending case (uplift(lift=1)-uplift(lift=0))

    Parameters:
    - upliftSimulation: The results of the uplift simulation (& delta to zero calculation uplift(lift=1)-uplift(lift=0)) 
    - responseModel: Class init of the responseModel
    - outputConfig: The type of change periods that apply to the ratio calculations
    - responseModel base configurations: The touchpoints

    Attributes:
    - deltaToZeroDict: Collecting all data necessary to calculate volume contribution
    - absoluteContributionCorrected: Corrected absolute result of delta to zero calculations
    - relativeContributions: Calculated relative contribution per influence factor


    '''

    def __init__(self, upliftSimulation, responseModel, outputConfig):


        #class instance from upliftSimulation containing the simulated uplifts and the configurations
        #class instance of responseModel
        self.upliftSimulation = upliftSimulation
        self.responseModel = responseModel

        #configurations
        self.outputConfig = outputConfig

        #collect all deltaToZeroSimulations for all subsets
        self.deltaToZeroDict = {}
        #collect all deltaToZero but with error correction
        self.absoluteContributionCorrected = {}
        #collect all relative contribution after error correction
        self.relativeContributions = {}

    def calculateVolumeContribution(self):
        '''
        The Volume contribution is calculated via the uplift simulations.
        Each influence factor (touchpoints, control variables, baseline) is added to a table 
        Sum of all factors represent the "gros" total contribution (gros because it is not equal to the true target value)
        This requires a relative delta error correction.
        
        '''
        
        for subset in self.upliftSimulation.outputConfig['CHANGE_PERIODS']:

            #collect all deltaToZero (lift(1)-lift(0) simulations (there is one for each touchpoint on a weekly level)
            #the sum should be close to the true sales for the respective week
            deltaToZeroSimulations=pd.DataFrame()
            
            #include volume contribution of each touchpoint
            for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:

                deltaToZeroSimulations[touchpoint] = self.upliftSimulation.deltaCurrentToZero[(subset,touchpoint)]

            #include basesales
            deltaToZeroSimulations['baseline'] = self.upliftSimulation.deltaBaseline

            #include sum - the variable to predict
            deltaToZeroSimulations['total_predict'] = deltaToZeroSimulations.sum(axis=1)
            
            #include the target
            deltaToZeroSimulations['total_target'] = self.responseModel.target

            #add the subset simulation table to the collection
            self.deltaToZeroDict[subset] = deltaToZeroSimulations


        return 0

    def correctContributionError(self):
        '''
        Since the sum of all simulated deltaContributions is not equal to the true target value,
        each factor will be adjusted with the relative delta error.
        '''

        for subset in self.upliftSimulation.outputConfig['CHANGE_PERIODS']:
            deltaToZeroCorrected=pd.DataFrame()

            
            #calculate error as (1+ (true_target-target_prediction)/target_prediction)
            error = (1+((self.deltaToZeroDict[subset]['total_target'] - self.deltaToZeroDict[subset]['total_predict'])/self.deltaToZeroDict[subset]['total_predict']))
            
            #multiply error with the predicted contribution for each factor

            #include touchpoints
            for touchpoint in self.responseModel.configurations['TOUCHPOINTS']:
                deltaToZeroCorrected[touchpoint] = error*self.deltaToZeroDict[subset][touchpoint]

            #include basesales
            deltaToZeroCorrected['baseline'] = error*self.deltaToZeroDict[subset]['baseline']

            #add the subset simulation table to the collection
            self.absoluteContributionCorrected[subset] = deltaToZeroCorrected
            
        #print the 'all weeks' delta to zero simulation (as it comes last) as a checking table
        deltaToZeroCorrected.to_csv('test_delta_corrected.csv')

    def calculateRelativeContribution(self):
        '''
        Calculate relative contribution for each subset based on the error corrected results
        '''

        for subset in self.upliftSimulation.outputConfig['CHANGE_PERIODS']:
            relativeContribution=pd.DataFrame()

            for item in self.outputConfig['CONTRIBUTORS']:
                relativeContribution[item] = self.absoluteContributionCorrected[subset][item]/self.absoluteContributionCorrected[subset].sum(axis=1)
            self.relativeContributions[subset] = relativeContribution



                

